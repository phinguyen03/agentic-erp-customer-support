import {
  Bot,
  CheckCircle,
  Clock3,
  Package,
  RefreshCw,
  RotateCcw,
  Settings,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useChatStore } from "@/stores/chatStore";
import type { ApiStatus } from "@/types/chat";

type SidebarProps = {
  apiStatus: ApiStatus;
};

const navItems = [
  { label: "Chat", icon: Bot, active: true },
  { label: "Approval status", icon: Clock3, active: false },
  { label: "Return policy", icon: Package, active: false },
  { label: "Settings", icon: Settings, active: false },
];

function getApiBadge(status: ApiStatus) {
  if (status === "connected") {
    return <Badge variant="success">Connected</Badge>;
  }

  if (status === "error") {
    return <Badge variant="destructive">Error</Badge>;
  }

  return <Badge variant="muted">Unknown</Badge>;
}

export function Sidebar({ apiStatus }: SidebarProps) {
  const email = useChatStore((state) => state.email);
  const clearMessages = useChatStore((state) => state.clearMessages);

  return (
    <aside className="hidden h-[calc(100dvh-2rem)] flex-col gap-4 lg:flex">
      <Card className="border-white/70 bg-white/88 shadow-panel backdrop-blur">
        <CardHeader className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-sm">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base">Agentic ERP Support</CardTitle>
              <p className="text-sm text-muted-foreground">Customer workflow assistant</p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <nav className="space-y-1">
            {navItems.map(({ icon: Icon, label, active }) => (
              <button
                key={label}
                type="button"
                className={`flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm transition-colors ${
                  active
                    ? "bg-primary/8 font-medium text-foreground"
                    : "text-muted-foreground hover:bg-slate-100 hover:text-foreground"
                }`}
              >
                <Icon className={`h-4 w-4 ${active ? "text-primary" : ""}`} />
                <span>{label}</span>
              </button>
            ))}
          </nav>

          <Separator />

          <div className="rounded-2xl border border-border/70 bg-slate-50/80 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Session</p>
            <p className="mt-2 break-all text-sm font-medium text-foreground">{email}</p>
          </div>

          <Card className="rounded-2xl border-border/70 bg-background shadow-none">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">System status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">API</span>
                {getApiBadge(apiStatus)}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Mode</span>
                <Badge variant="outline">Streaming</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Health check</span>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <CheckCircle className="h-3.5 w-3.5" />
                  Background polling
                </div>
              </div>
            </CardContent>
          </Card>

          <Button variant="outline" className="w-full rounded-2xl" onClick={clearMessages}>
            <RotateCcw className="h-4 w-4" />
            Clear conversation
          </Button>
          <Button variant="ghost" className="w-full rounded-2xl text-muted-foreground">
            <RefreshCw className="h-4 w-4" />
            Live updates enabled
          </Button>
        </CardContent>
      </Card>
    </aside>
  );
}
