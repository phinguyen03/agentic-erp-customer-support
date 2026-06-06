import { Send } from "lucide-react";
import type { KeyboardEvent } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type ChatInputProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
};

export function ChatInput({ value, onChange, onSubmit, disabled }: ChatInputProps) {
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="sticky bottom-0 z-10 border-t border-border/70 bg-background/85 px-4 pb-4 pt-4 backdrop-blur xl:px-6">
      <div className="mx-auto max-w-4xl rounded-[28px] border border-border/70 bg-white/95 p-3 shadow-soft">
        <div className="flex flex-col gap-3">
          <label htmlFor="chat-message" className="sr-only">
            Message support assistant
          </label>
          <Textarea
            id="chat-message"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Describe your return, refund, exchange, or approval question."
            className={cn(
              "max-h-44 min-h-[96px] resize-none border-0 bg-transparent p-2 shadow-none focus-visible:ring-0",
              disabled && "cursor-not-allowed",
            )}
            aria-label="Message support assistant"
          />
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs text-muted-foreground">Press Enter to send. Use Shift+Enter for a new line.</p>
            <Button
              onClick={onSubmit}
              disabled={disabled || !value.trim()}
              size="lg"
              className="rounded-2xl px-5"
              aria-label="Send message"
            >
              <Send className="h-4 w-4" />
              Send
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
