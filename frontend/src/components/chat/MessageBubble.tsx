import { AlertCircle, Bot, RefreshCw, User } from "lucide-react";

import { StructuredDataCard } from "@/components/chat/StructuredDataCard";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { Button } from "@/components/ui/button";
import { cn, formatTimestamp } from "@/lib/utils";
import type { ChatMessage } from "@/types/chat";

type MessageBubbleProps = {
  message: ChatMessage;
  onRetry?: (assistantMessageId: string) => void;
};

function normalizeStructuredData(data: unknown) {
  if (typeof data === "undefined") {
    return [];
  }

  return Array.isArray(data) ? data : [data];
}

export function MessageBubble({ message, onRetry }: MessageBubbleProps) {
  if (message.role === "system") {
    return (
      <div className="flex justify-center">
        <div className="rounded-full border border-border/70 bg-background px-3 py-1.5 text-xs text-muted-foreground">
          {message.content}
        </div>
      </div>
    );
  }

  const isUser = message.role === "user";
  const structuredItems = normalizeStructuredData(message.structuredData);

  return (
    <div className={cn("flex w-full animate-fade-up", isUser ? "justify-end" : "justify-start")}>
      <div className={cn("max-w-[88%] space-y-3 sm:max-w-[80%]", isUser && "items-end")}>
        <div className={cn("flex items-center gap-2 text-xs text-muted-foreground", isUser && "justify-end")}>
          <span
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-2xl border border-border/70",
              isUser ? "bg-primary/10 text-primary" : "bg-slate-100 text-slate-700",
            )}
          >
            {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
          </span>
          <span>{isUser ? "You" : "Assistant"}</span>
          <span>{formatTimestamp(message.createdAt)}</span>
        </div>
        <div
          className={cn(
            "rounded-[28px] border px-5 py-4 shadow-sm",
            isUser
              ? "border-primary/20 bg-primary text-primary-foreground"
              : "border-border/70 bg-white text-foreground",
          )}
        >
          {message.status === "streaming" && !message.content ? (
            <TypingIndicator />
          ) : (
            <p className="whitespace-pre-wrap text-sm leading-7">{message.content}</p>
          )}
        </div>
        {structuredItems.length > 0 && (
          <div className="space-y-3">
            {structuredItems.map((item, index) => (
              <StructuredDataCard key={`${message.id}-data-${index}`} payload={item} />
            ))}
          </div>
        )}
        {message.status === "error" && (
          <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            <AlertCircle className="h-4 w-4" />
            <span>This response failed. You can retry the last request.</span>
            {onRetry ? (
              <Button
                variant="outline"
                size="sm"
                className="border-rose-200 bg-white text-rose-700 hover:bg-rose-100"
                onClick={() => onRetry(message.id)}
              >
                <RefreshCw className="h-4 w-4" />
                Retry
              </Button>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}
