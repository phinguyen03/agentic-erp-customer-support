export function TypingIndicator() {
  return (
    <div className="inline-flex items-center gap-1.5 rounded-full border border-border/70 bg-background/80 px-3 py-2 text-xs text-muted-foreground">
      <span className="sr-only">Assistant is thinking</span>
      <span className="h-2 w-2 animate-pulse-dot rounded-full bg-primary [animation-delay:-0.3s]" />
      <span className="h-2 w-2 animate-pulse-dot rounded-full bg-primary [animation-delay:-0.15s]" />
      <span className="h-2 w-2 animate-pulse-dot rounded-full bg-primary" />
      <span className="ml-1">Assistant is thinking</span>
    </div>
  );
}
