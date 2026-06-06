import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { ChatMessage, ChatState } from "@/types/chat";

type PersistedChatState = Pick<ChatState, "email" | "messages">;

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      email: null,
      messages: [],
      isStreaming: false,
      error: null,
      setEmail: (email) => set({ email, error: null }),
      clearEmail: () =>
        set({
          email: null,
          messages: [],
          error: null,
          isStreaming: false,
        }),
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),
      updateMessage: (id, patch) =>
        set((state) => ({
          messages: state.messages.map((message) =>
            message.id === id ? { ...message, ...patch } : message,
          ),
        })),
      clearMessages: () => set({ messages: [], error: null }),
      setStreaming: (value) => set({ isStreaming: value }),
      setError: (error) => set({ error }),
    }),
    {
      name: "agentic-erp-support",
      partialize: (state): PersistedChatState => ({
        email: state.email,
        messages: state.messages.slice(-30),
      }),
    },
  ),
);

export function getChatMessageById(messages: ChatMessage[], id: string) {
  return messages.find((message) => message.id === id);
}
