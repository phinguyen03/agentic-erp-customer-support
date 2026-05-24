import { BadgeDollarSign, Clock3, Package, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

type EmptyStateProps = {
  onSelectPrompt: (prompt: string) => void;
};

const prompts = [
  {
    icon: RotateCcw,
    label: "Return request",
    prompt: "I want to return my order",
  },
  {
    icon: BadgeDollarSign,
    label: "Refund request",
    prompt: "I want a refund for ord_1001",
  },
  {
    icon: Clock3,
    label: "Approval status",
    prompt: "What is the status of my approval?",
  },
  {
    icon: Package,
    label: "Exchange request",
    prompt: "I want to exchange an item",
  },
];

export function EmptyState({ onSelectPrompt }: EmptyStateProps) {
  return (
    <Card className="overflow-hidden border-dashed border-border/80 bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.08),transparent_42%),linear-gradient(180deg,rgba(255,255,255,0.98),rgba(248,250,252,0.92))] shadow-none">
      <CardContent className="flex flex-col gap-8 p-8 sm:p-10">
        <div className="max-w-2xl space-y-3">
          <div className="inline-flex items-center rounded-full border border-primary/15 bg-primary/5 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-primary">
            AI workflow assistant
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
              Start a support conversation with a workflow-aware assistant.
            </h2>
            <p className="text-sm leading-7 text-muted-foreground sm:text-base">
              This interface is optimized for returns, refunds, exchanges, approval checks, and unsupported
              requests that need escalation.
            </p>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          {prompts.map(({ icon: Icon, label, prompt }) => (
            <Button
              key={prompt}
              variant="outline"
              className="h-auto justify-start rounded-2xl border-border/70 px-4 py-4 text-left hover:border-primary/25 hover:bg-white"
              onClick={() => onSelectPrompt(prompt)}
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-100 text-slate-700">
                <Icon className="h-4 w-4" />
              </span>
              <span className="flex flex-col items-start">
                <span className="text-sm font-semibold text-foreground">{label}</span>
                <span className="text-sm text-muted-foreground">{prompt}</span>
              </span>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
