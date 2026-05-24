import { AlertCircle, Bot } from "lucide-react";

import { ChatWindow } from "@/components/chat/ChatWindow";
import { RightInfoPanel } from "@/components/layout/RightInfoPanel";
import { Sidebar } from "@/components/layout/Sidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useChatStore } from "@/stores/chatStore";
import type { ApiStatus } from "@/types/chat";

type AppShellProps = {
  apiStatus: ApiStatus;
};

export function AppShell({ apiStatus }: AppShellProps) {
  const clearEmail = useChatStore((state) => state.clearEmail);

  return (
    <main className="min-h-[100dvh] bg-[linear-gradient(180deg,#f7fbff_0%,#f8fafc_40%,#f5f7fb_100%)] px-4 py-4 sm:px-6 lg:px-8">
      <div className="absolute inset-0 hidden bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.08),transparent_24%),radial-gradient(circle_at_bottom_right,rgba(37,99,235,0.07),transparent_28%)] lg:block" />
      <div className="relative mx-auto flex max-w-[1600px] flex-col gap-4 lg:grid lg:grid-cols-[280px_minmax(0,1fr)] xl:grid-cols-[280px_minmax(0,1fr)_320px]">
        <Sidebar apiStatus={apiStatus} />

        <div className="space-y-4">
          <Card className="border-white/70 bg-white/88 shadow-soft lg:hidden">
            <CardContent className="flex flex-wrap items-center justify-between gap-3 p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
                  <Bot className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">Agentic ERP Support</p>
                  <p className="text-xs text-muted-foreground">Streaming workflow assistant</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge
                  variant={apiStatus === "connected" ? "success" : apiStatus === "error" ? "destructive" : "muted"}
                >
                  API {apiStatus}
                </Badge>
                <Button variant="outline" size="sm" className="rounded-xl" onClick={clearEmail}>
                  <AlertCircle className="h-4 w-4" />
                  Change email
                </Button>
              </div>
            </CardContent>
          </Card>

          <ChatWindow onChangeEmail={clearEmail} />
        </div>

        <RightInfoPanel />
      </div>
    </main>
  );
}
