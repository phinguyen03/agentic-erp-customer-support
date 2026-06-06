export type ParsedSSEEvent = {
  data: string;
  json: unknown | null;
  isDone: boolean;
  isInvalidJson: boolean;
};

function parseEventBlock(block: string): ParsedSSEEvent | null {
  const lines = block
    .split("\n")
    .map((line) => line.trimEnd())
    .filter(Boolean);

  if (lines.length === 0) {
    return null;
  }

  const dataLines = lines
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trim());

  if (dataLines.length === 0) {
    return null;
  }

  const data = dataLines.join("\n").trim();

  if (!data) {
    return null;
  }

  if (data === "[DONE]") {
    return {
      data,
      json: null,
      isDone: true,
      isInvalidJson: false,
    };
  }

  try {
    return {
      data,
      json: JSON.parse(data),
      isDone: false,
      isInvalidJson: false,
    };
  } catch {
    return {
      data,
      json: null,
      isDone: false,
      isInvalidJson: true,
    };
  }
}

export function createSSEParser() {
  let buffer = "";

  const parseBuffer = (flush: boolean) => {
    const normalized = buffer.replace(/\r\n/g, "\n");
    const blocks = normalized.split("\n\n");

    if (!flush) {
      buffer = blocks.pop() ?? "";
    } else {
      buffer = "";
    }

    return blocks
      .map((block) => parseEventBlock(block))
      .filter((event): event is ParsedSSEEvent => event !== null);
  };

  return {
    push(chunk: string) {
      buffer += chunk;
      return parseBuffer(false);
    },
    flush() {
      if (!buffer.trim()) {
        buffer = "";
        return [] as ParsedSSEEvent[];
      }

      return parseBuffer(true);
    },
  };
}
