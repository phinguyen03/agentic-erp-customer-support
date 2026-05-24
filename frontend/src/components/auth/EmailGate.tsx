import { ArrowRight, Bot, ShieldCheck, Sparkles } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useChatStore } from "@/stores/chatStore";

const exampleEmails = ["anna@example.com", "ben@example.com"];

function isValidEmail(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

export function EmailGate() {
  const currentEmail = useChatStore((state) => state.email);
  const setEmail = useChatStore((state) => state.setEmail);
  const [email, setEmailInput] = useState(currentEmail ?? "");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = () => {
    const nextEmail = email.trim().toLowerCase();

    if (!nextEmail) {
      setError("Email is required to open a support session.");
      return;
    }

    if (!isValidEmail(nextEmail)) {
      setError("Enter a valid email address to continue.");
      return;
    }

    setEmail(nextEmail);
    setError(null);
  };

  return (
    <main className="relative min-h-[100dvh] overflow-hidden bg-[linear-gradient(180deg,#f8fbff_0%,#f8fafc_45%,#eef4ff_100%)] px-4 py-8 sm:px-6 lg:px-8">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.12),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(37,99,235,0.12),transparent_32%)]" />
      <div className="relative mx-auto grid min-h-[calc(100dvh-4rem)] max-w-6xl items-center gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <section className="space-y-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/15 bg-white/80 px-4 py-2 text-sm font-medium text-primary shadow-sm backdrop-blur">
            <Bot className="h-4 w-4" />
            Agentic ERP Customer Support
          </div>
          <div className="max-w-2xl space-y-4">
            <h1 className="text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
              Workflow-driven support for returns, refunds, exchanges, and approvals.
            </h1>
            <p className="max-w-xl text-base leading-8 text-slate-600 sm:text-lg">
              Start with a customer email, then hand the conversation to an AI assistant designed for ERP-style
              support flows and structured approval handling.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            <Card className="border-white/70 bg-white/80 shadow-soft">
              <CardContent className="space-y-3 p-5">
                <Sparkles className="h-5 w-5 text-primary" />
                <div>
                  <h2 className="font-medium text-slate-900">Streaming responses</h2>
                  <p className="mt-1 text-sm leading-6 text-slate-600">Live workflow updates over a POST-based SSE stream.</p>
                </div>
              </CardContent>
            </Card>
            <Card className="border-white/70 bg-white/80 shadow-soft">
              <CardContent className="space-y-3 p-5">
                <ShieldCheck className="h-5 w-5 text-primary" />
                <div>
                  <h2 className="font-medium text-slate-900">Approval aware</h2>
                  <p className="mt-1 text-sm leading-6 text-slate-600">Handles auto-approvals and manager review updates cleanly.</p>
                </div>
              </CardContent>
            </Card>
            <Card className="border-white/70 bg-white/80 shadow-soft">
              <CardContent className="space-y-3 p-5">
                <Bot className="h-5 w-5 text-primary" />
                <div>
                  <h2 className="font-medium text-slate-900">Customer-ready UI</h2>
                  <p className="mt-1 text-sm leading-6 text-slate-600">Built for practical support use, not as a throwaway demo.</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        <Card className="border-white/80 bg-white/88 shadow-panel backdrop-blur">
          <CardHeader className="space-y-2">
            <CardTitle className="text-2xl text-slate-950">Open a support session</CardTitle>
            <CardDescription className="text-sm leading-6 text-slate-600">
              Use a customer email to continue into the support workspace.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-slate-800">
                Customer email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmailInput(event.target.value)}
                placeholder="anna@example.com"
                aria-invalid={Boolean(error)}
                aria-describedby={error ? "email-error" : undefined}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    handleSubmit();
                  }
                }}
              />
              {error ? (
                <p id="email-error" className="text-sm text-rose-600">
                  {error}
                </p>
              ) : (
                <p className="text-sm text-slate-500">Session email is saved locally so returning customers can pick up quickly.</p>
              )}
            </div>
            <div className="space-y-3">
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">Quick examples</p>
              <div className="flex flex-wrap gap-2">
                {exampleEmails.map((exampleEmail) => (
                  <Button
                    key={exampleEmail}
                    variant="outline"
                    className="rounded-full border-border/70 bg-white"
                    onClick={() => {
                      setEmailInput(exampleEmail);
                      setError(null);
                    }}
                  >
                    {exampleEmail}
                  </Button>
                ))}
              </div>
            </div>
            <Button onClick={handleSubmit} size="lg" className="w-full rounded-2xl">
              Continue
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
