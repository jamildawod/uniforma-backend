"use client";

import { useQuery } from "@tanstack/react-query";

import {
  fetchDataQuality,
  fetchOverrideConflicts,
  fetchSyncHealth,
  fetchSystemHealth,
  type IntelligencePagination
} from "@/lib/api/intelligence";

export const intelligenceQueryKeys = {
  root: ["intelligence"] as const,
  systemHealth: () => [...intelligenceQueryKeys.root, "system-health"] as const,
  dataQuality: () => [...intelligenceQueryKeys.root, "data-quality"] as const,
  syncHealth: (params: IntelligencePagination) =>
    [...intelligenceQueryKeys.root, "sync-health", params.page ?? 1, params.pageSize ?? 10] as const,
  overrideConflicts: (params: IntelligencePagination) =>
    [...intelligenceQueryKeys.root, "override-conflicts", params.page ?? 1, params.pageSize ?? 10] as const
};

const sharedQueryOptions = {
  staleTime: 60_000,
  gcTime: 5 * 60_000,
  retry: 2 as const
};

export function useSystemHealth() {
  return useQuery({
    queryKey: intelligenceQueryKeys.systemHealth(),
    queryFn: fetchSystemHealth,
    ...sharedQueryOptions
  });
}

export function useDataQuality() {
  return useQuery({
    queryKey: intelligenceQueryKeys.dataQuality(),
    queryFn: fetchDataQuality,
    ...sharedQueryOptions
  });
}

export function useSyncHealth(params: IntelligencePagination = {}) {
  return useQuery({
    queryKey: intelligenceQueryKeys.syncHealth(params),
    queryFn: () => fetchSyncHealth(params),
    ...sharedQueryOptions
  });
}

export function useOverrideConflicts(params: IntelligencePagination = {}) {
  return useQuery({
    queryKey: intelligenceQueryKeys.overrideConflicts(params),
    queryFn: () => fetchOverrideConflicts(params),
    ...sharedQueryOptions
  });
}
