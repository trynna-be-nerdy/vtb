"use client";

import { HeroUIProvider } from "@heroui/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: { staleTime: 1000 * 60 * 15 }, // 15 min
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      <HeroUIProvider>{children}</HeroUIProvider>
    </QueryClientProvider>
  );
}
