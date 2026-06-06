import { useCallback } from "react";

import { sendChatMessage, streamChatMessage } from "@/lib/api";
import { createMessageId, getErrorMessage } from "@/lib/utils";
import { getChatMessageById, useChatStore } from "@/stores/chatStore";
import type { ChatMessage } from "@/types/chat";

function mergeAssistantContent(current: string, incoming: string) {
  if (!current) {
    return incoming;
  }

  if (incoming === current) {
    return current;
  }

  if (incoming.startsWith(current)) {
    return incoming;
  }

  if (current.endsWith(incoming)) {
    return current;
  }

  return `${current}${current.endsWith("\n") ? "\n" : "\n\n"}${incoming}`;
}

function mergeStructuredData(current: unknown, nextPayload: unknown) {
  if (typeof current === "undefined") {
    return nextPayload;
  }

  if (Array.isArray(current)) {
    return [...current, nextPayload];
  }

  return [current, nextPayload];
}

export function useChatStream() {
  const email = useChatStore((state) => state.email);
  const messages = useChatStore((state) => state.messages);
  const addMessage = useChatStore((state) => state.addMessage);
  const updateMessage = useChatStore((state) => state.updateMessage);
  const setStreaming = useChatStore((state) => state.setStreaming);
  const setError = useChatStore((state) => state.setError);

  const runStreamingRequest = useCallback(
    async (targetEmail: string, prompt: string, assistantId: string) => {
      let assistantContent = "";

      await streamChatMessage({
        email: targetEmail,
        message: prompt,
        onMessage: (content) => {
          assistantContent = mergeAssistantContent(assistantContent, content);
          updateMessage(assistantId, {
            content: assistantContent,
            status: "streaming",
          });
        },
        onData: (payload) => {
          const currentMessage = getChatMessageById(useChatStore.getState().messages, assistantId);
          updateMessage(assistantId, {
            structuredData: mergeStructuredData(currentMessage?.structuredData, payload),
          });
        },
        onDone: () => {
          updateMessage(assistantId, {
            status: "sent",
          });
          setStreaming(false);
          setError(null);
        },
        onError: async (error) => {
          if (!assistantContent) {
            try {
              const fallback = await sendChatMessage(targetEmail, prompt);
              assistantContent = fallback.message;
              updateMessage(assistantId, {
                content: assistantContent,
                status: "sent",
              });
              setStreaming(false);
              setError(null);
              return;
            } catch (fallbackError) {
              const message = getErrorMessage(fallbackError);
              updateMessage(assistantId, {
                content: "The support response was interrupted before it completed.",
                status: "error",
              });
              setStreaming(false);
              setError(message);
              return;
            }
          }

          updateMessage(assistantId, {
            status: "error",
          });
          setStreaming(false);
          setError(getErrorMessage(error));
        },
      });
    },
    [setError, setStreaming, updateMessage],
  );

  const sendMessage = useCallback(
    async (rawMessage: string) => {
      const prompt = rawMessage.trim();

      if (!email) {
        setError("Enter a customer email before starting the conversation.");
        return;
      }

      if (!prompt) {
        return;
      }

      const createdAt = new Date().toISOString();
      const userId = createMessageId();
      const assistantId = createMessageId();

      const userMessage: ChatMessage = {
        id: userId,
        role: "user",
        content: prompt,
        createdAt,
        status: "sent",
      };

      const assistantMessage: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        createdAt,
        status: "streaming",
        linkedMessageId: userId,
      };

      addMessage(userMessage);
      addMessage(assistantMessage);
      setStreaming(true);
      setError(null);

      await runStreamingRequest(email, prompt, assistantId);
    },
    [addMessage, email, runStreamingRequest, setError, setStreaming],
  );

  const retryMessage = useCallback(
    async (assistantMessageId?: string) => {
      if (!email) {
        setError("Enter a customer email before retrying the request.");
        return;
      }

      const state = useChatStore.getState();
      const targetMessage =
        (assistantMessageId
          ? getChatMessageById(state.messages, assistantMessageId)
          : [...state.messages].reverse().find((message) => message.role === "assistant" && message.status === "error")) ??
        null;

      if (!targetMessage) {
        return;
      }

      const targetIndex = state.messages.findIndex((message) => message.id === targetMessage.id);
      const linkedUserMessage =
        (targetMessage.linkedMessageId
          ? getChatMessageById(state.messages, targetMessage.linkedMessageId)
          : null) ??
        [...state.messages].slice(0, targetIndex).reverse().find((message) => message.role === "user");

      if (!linkedUserMessage?.content) {
        setError("The original request could not be recovered for retry.");
        return;
      }

      updateMessage(targetMessage.id, {
        content: "",
        structuredData: undefined,
        status: "streaming",
      });
      setStreaming(true);
      setError(null);

      await runStreamingRequest(email, linkedUserMessage.content, targetMessage.id);
    },
    [email, runStreamingRequest, setError, setStreaming, updateMessage],
  );

  return {
    messages,
    sendMessage,
    retryMessage,
  };
}
