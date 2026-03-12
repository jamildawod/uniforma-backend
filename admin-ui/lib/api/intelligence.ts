import { apiFetch } from "@/lib/api/client";
import type {
  DataQualityResponse,
  OverrideConflictResponse,
  SyncHealthResponse,
  SystemHealth
} from "@/types/intelligence";

export interface IntelligencePagination {
  page?: number;
  pageSize?: number;
}

export function fetchSystemHealth(): Promise<SystemHealth> {
  return apiFetch<SystemHealth>("/api/uniforma/api/v1/admin/intelligence/summary");
}

export function fetchDataQuality(): Promise<DataQualityResponse> {
  return apiFetch<DataQualityResponse>("/api/uniforma/api/v1/admin/intelligence/data-quality");
}

export function fetchSyncHealth(params: IntelligencePagination = {}): Promise<SyncHealthResponse> {
  return apiFetch<SyncHealthResponse>("/api/uniforma/api/v1/admin/intelligence/sync-health", {
    query: {
      page: params.page ?? 1,
      page_size: params.pageSize ?? 10
    }
  });
}

export function fetchOverrideConflicts(
  params: IntelligencePagination = {}
): Promise<OverrideConflictResponse> {
  return apiFetch<OverrideConflictResponse>("/api/uniforma/api/v1/admin/intelligence/override-conflicts", {
    query: {
      page: params.page ?? 1,
      page_size: params.pageSize ?? 10
    }
  });
}
