import { AlertCircle, LogOut } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { ChatInput } from "@/components/chat/ChatInput";
import { EmptyState } from "@/components/chat/EmptyState";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChatStream } from "@/hooks/useChatStream";
import { useChatStore } from "@/stores/chatStore";

type ChatWindowProps = {
  onChangeEmail: () => void;
};

export function ChatWindow({ onChangeEmail }: ChatWindowProps) {
  const email = useChatStore((state) => state.email);
  const isStreaming = useChatStore((state) => state.isStreaming);
  const error = useChatStore((state) => state.error);
  const { messages, sendMessage, retryMessage } = useChatStream();
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  const handleSubmit = async () => {
    const next = draft.trim();
    if (!next) {
      return;
    }

    setDraft("");
    await sendMessage(next);
  };

  const handlePrompt = async (prompt: string) => {
    if (isStreaming) {
      return;
    }

    await sendMessage(prompt);
  };

  return (
    <section className="flex min-h-[100dvh] flex-col rounded-[32px] border border-white/50 bg-white/80 shadow-panel backdrop-blur xl:min-h-[calc(100dvh-2rem)]">
      <header className="border-b border-border/70 px-4 py-5 sm:px-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl font-semibold tracking-tight text-foreground sm:text-2xl">Agentic ERP Support</h1>
              <Badge variant="outline" className="border-primary/15 bg-primary/5 text-primary">
                Streaming workflows
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              Returns, refunds, exchanges, and approval workflows
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="rounded-2xl border border-border/70 bg-background px-4 py-2 text-sm text-muted-foreground">
              Customer <span className="font-medium text-foreground">{email}</span>
            </div>
            <Button variant="outline" className="rounded-2xl" onClick={onChangeEmail}>
              <LogOut className="h-4 w-4" />
              Change email
            </Button>
          </div>
        </div>
      </header>

      {error ? (
        <div className="border-b border-rose-200 bg-rose-50/90 px-4 py-3 text-sm text-rose-700 sm:px-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-4 w-4 flex-none" />
            <span>{error}</span>
          </div>
        </div>
      ) : null}

      <ScrollArea className="flex-1 px-4 py-4 sm:px-6">
        <div className="mx-auto flex max-w-4xl flex-col gap-6 pb-8">
          {messages.length === 0 ? (
            <EmptyState onSelectPrompt={handlePrompt} />
          ) : (
            messages.map((message) => (
              <MessageBubble key={message.id} message={message} onRetry={retryMessage} />
            ))
          )}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <ChatInput value={draft} onChange={setDraft} onSubmit={handleSubmit} disabled={isStreaming} />
    </section>
  );
}
