import { BadgeDollarSign, Clock3, Package, RefreshCcw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const capabilities = [
  "Start return, refund, and exchange requests",
  "Check approval status on manager-routed cases",
  "Handle unsupported requests with escalation language",
];

const rules = [
  "30-day return window",
  "Good condition required",
  "Orders under $50 are auto-approved",
  "Orders $50 or more require manager approval",
];

export function RightInfoPanel() {
  return (
    <aside className="hidden h-[calc(100dvh-2rem)] flex-col gap-4 xl:flex">
      <Card className="border-white/70 bg-white/88 shadow-panel backdrop-blur">
        <CardHeader className="space-y-2">
          <Badge variant="outline" className="w-fit border-primary/15 bg-primary/5 text-primary">
            Support guide
          </Badge>
          <CardTitle className="text-lg">What this assistant can do</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            {capabilities.map((item) => (
              <div key={item} className="rounded-2xl border border-border/70 bg-background px-4 py-3 text-sm text-foreground">
                {item}
              </div>
            ))}
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-medium text-foreground">Example requests</h3>
            <div className="space-y-2">
              <div className="flex items-start gap-3 rounded-2xl border border-border/70 bg-slate-50/80 p-4">
                <RefreshCcw className="mt-0.5 h-4 w-4 text-primary" />
                <p className="text-sm text-muted-foreground">“I want to return my order”</p>
              </div>
              <div className="flex items-start gap-3 rounded-2xl border border-border/70 bg-slate-50/80 p-4">
                <BadgeDollarSign className="mt-0.5 h-4 w-4 text-primary" />
                <p className="text-sm text-muted-foreground">“I want a refund for ord_1001”</p>
              </div>
              <div className="flex items-start gap-3 rounded-2xl border border-border/70 bg-slate-50/80 p-4">
                <Clock3 className="mt-0.5 h-4 w-4 text-primary" />
                <p className="text-sm text-muted-foreground">“What is the status of my approval?”</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-medium text-foreground">Business rules summary</h3>
            <div className="space-y-2">
              {rules.map((rule) => (
                <div key={rule} className="flex items-center gap-3 rounded-2xl border border-border/70 bg-background px-4 py-3 text-sm">
                  <Package className="h-4 w-4 text-primary" />
                  <span className="text-muted-foreground">{rule}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </aside>
  );
}
