import { AlertCircle, BadgeDollarSign, CheckCircle2, Clock3, Package } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency, isRecord } from "@/lib/utils";

type StructuredDataCardProps = {
  payload: unknown;
};

function getStatusVariant(status: unknown): "success" | "warning" | "destructive" | "muted" {
  if (typeof status !== "string") {
    return "muted";
  }

  const normalized = status.toLowerCase();

  if (normalized === "approved") {
    return "success";
  }

  if (normalized === "pending") {
    return "warning";
  }

  if (normalized === "declined") {
    return "destructive";
  }

  return "muted";
}

function isApprovalPayload(payload: unknown): payload is Record<string, unknown> {
  if (!isRecord(payload)) {
    return false;
  }

  return ["request_id", "order_id", "action", "amount", "status"].some((key) => key in payload);
}

function ApprovalSummary({ payload }: { payload: Record<string, unknown> }) {
  const amount =
    typeof payload.amount === "number"
      ? payload.amount
      : typeof payload.amount === "string"
        ? Number(payload.amount)
        : null;

  return (
    <Card className="rounded-2xl border-primary/10 bg-gradient-to-br from-white via-white to-slate-50 shadow-none">
      <CardHeader className="space-y-4 pb-4">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1">
            <CardTitle className="text-base">Approval workflow update</CardTitle>
            <p className="text-sm text-muted-foreground">
              Structured workflow data was returned by the backend for this request.
            </p>
          </div>
          <Badge variant={getStatusVariant(payload.status)}>
            {typeof payload.status === "string" ? payload.status : "unknown"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="grid gap-3 pb-5">
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
            <div className="mb-1 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
              <Package className="h-3.5 w-3.5" />
              Order
            </div>
            <div className="text-sm font-medium text-foreground">
              {typeof payload.order_id === "string" ? payload.order_id : "Unavailable"}
            </div>
          </div>
          <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
            <div className="mb-1 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
              <BadgeDollarSign className="h-3.5 w-3.5" />
              Amount
            </div>
            <div className="text-sm font-medium text-foreground">
              {Number.isFinite(amount) ? formatCurrency(amount as number) : "Unavailable"}
            </div>
          </div>
          <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
            <div className="mb-1 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Action
            </div>
            <div className="text-sm font-medium capitalize text-foreground">
              {typeof payload.action === "string" ? payload.action.replace(/_/g, " ") : "Unavailable"}
            </div>
          </div>
          <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
            <div className="mb-1 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
              <Clock3 className="h-3.5 w-3.5" />
              Request ID
            </div>
            <div className="text-sm font-medium text-foreground">
              {typeof payload.request_id === "string" ? payload.request_id : "Unavailable"}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function StructuredDataCard({ payload }: StructuredDataCardProps) {
  if (isApprovalPayload(payload)) {
    return <ApprovalSummary payload={payload} />;
  }

  return (
    <Card className="rounded-2xl border-dashed border-border/80 bg-slate-50/70 shadow-none">
      <CardContent className="p-4">
        <details className="group">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-medium text-foreground">
            <span className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
              Structured backend payload
            </span>
            <span className="text-xs text-muted-foreground group-open:hidden">Expand</span>
            <span className="hidden text-xs text-muted-foreground group-open:block">Collapse</span>
          </summary>
          <pre className="mt-3 overflow-x-auto rounded-2xl border border-border/70 bg-background p-3 text-xs leading-6 text-slate-700">
            {JSON.stringify(payload, null, 2)}
          </pre>
        </details>
      </CardContent>
    </Card>
  );
}
