export type MessageRole = "user" | "assistant" | "system";
export type MessageStatus = "sending" | "streaming" | "sent" | "error";

export type ChatMessage = {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  status?: MessageStatus;
  structuredData?: unknown;
  linkedMessageId?: string;
};

export type ChatState = {
  email: string | null;
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
  setEmail: (email: string) => void;
  clearEmail: () => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, patch: Partial<ChatMessage>) => void;
  clearMessages: () => void;
  setStreaming: (value: boolean) => void;
  setError: (error: string | null) => void;
};

export type StreamEnvelope =
  | { type: "message"; content: string }
  | { type: "data"; payload: unknown }
  | { type: "done" };

export type ApiStatus = "unknown" | "connected" | "error";
