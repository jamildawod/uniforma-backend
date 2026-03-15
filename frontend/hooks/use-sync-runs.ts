"use client";

import { useQuery } from "@tanstack/react-query";

import { getSyncRuns } from "@/lib/api/client";

export function useSyncRuns() {
  return useQuery({
    queryKey: ["sync-runs"],
    queryFn: getSyncRuns
  });
}
