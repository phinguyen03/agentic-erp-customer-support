import { createSSEParser } from "@/lib/sse";
import { getErrorMessage, isRecord } from "@/lib/utils";
import type { ApiStatus } from "@/types/chat";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type StreamChatMessageParams = {
  email: string;
  message: string;
  onMessage: (content: string) => void;
  onData?: (payload: unknown) => void;
  onDone?: () => void;
  onError?: (error: Error) => void;
};

function buildUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

async function readErrorMessage(response: Response) {
  try {
    const contentType = response.headers.get("content-type") ?? "";

    if (contentType.includes("application/json")) {
      const json = (await response.json()) as unknown;
      if (isRecord(json) && typeof json.detail === "string") {
        return json.detail;
      }
    }

    const text = await response.text();
    return text || `Request failed with status ${response.status}.`;
  } catch {
    return `Request failed with status ${response.status}.`;
  }
}

export async function sendChatMessage(email: string, message: string): Promise<{ message: string }> {
  const response = await fetch(buildUrl("/api/v1/chat"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, message }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as { message: string };
}

export async function streamChatMessage({
  email,
  message,
  onMessage,
  onData,
  onDone,
  onError,
}: StreamChatMessageParams): Promise<void> {
  try {
    const response = await fetch(buildUrl("/api/v1/chat/stream"), {
      method: "POST",
      headers: {
        Accept: "text/event-stream",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, message }),
    });

    if (!response.ok) {
      throw new Error(await readErrorMessage(response));
    }

    if (!response.body) {
      const fallback = await sendChatMessage(email, message);
      onMessage(fallback.message);
      onDone?.();
      return;
    }

    const parser = createSSEParser();
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let completed = false;

    const processEvent = (rawEvent: unknown) => {
      if (!isRecord(rawEvent) || typeof rawEvent.type !== "string") {
        return;
      }

      if (rawEvent.type === "message" && typeof rawEvent.content === "string") {
        onMessage(rawEvent.content);
        return;
      }

      if (rawEvent.type === "data") {
        onData?.(rawEvent.payload);
        return;
      }

      if (rawEvent.type === "done") {
        completed = true;
        onDone?.();
      }
    };

    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      const events = parser.push(chunk);

      for (const event of events) {
        if (event.isDone) {
          completed = true;
          onDone?.();
          return;
        }

        if (event.isInvalidJson || event.json === null) {
          continue;
        }

        processEvent(event.json);
        if (completed) {
          return;
        }
      }
    }

    const remainingEvents = parser.flush();
    for (const event of remainingEvents) {
      if (event.isDone) {
        completed = true;
        onDone?.();
        break;
      }

      if (event.isInvalidJson || event.json === null) {
        continue;
      }

      processEvent(event.json);
      if (completed) {
        break;
      }
    }

    if (!completed) {
      onDone?.();
    }
  } catch (error) {
    const normalized = new Error(getErrorMessage(error));
    onError?.(normalized);
  }
}

export async function getApiStatus(): Promise<ApiStatus> {
  try {
    const response = await fetch(buildUrl("/api/v1/health"));
    return response.ok ? "connected" : "error";
  } catch {
    return "error";
  }
}
