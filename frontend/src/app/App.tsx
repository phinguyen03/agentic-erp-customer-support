import { useEffect, useState } from "react";

import { EmailGate } from "@/components/auth/EmailGate";
import { AppShell } from "@/components/layout/AppShell";
import { getApiStatus } from "@/lib/api";
import { useChatStore } from "@/stores/chatStore";
import type { ApiStatus } from "@/types/chat";

export default function App() {
  const email = useChatStore((state) => state.email);
  const [apiStatus, setApiStatus] = useState<ApiStatus>("unknown");

  useEffect(() => {
    let active = true;

    const checkHealth = async () => {
      const status = await getApiStatus();
      if (active) {
        setApiStatus(status);
      }
    };

    void checkHealth();
    const intervalId = window.setInterval(() => {
      void checkHealth();
    }, 45000);

    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, []);

  if (!email) {
    return <EmailGate />;
  }

  return <AppShell apiStatus={apiStatus} />;
}
