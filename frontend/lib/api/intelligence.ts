import { apiFetch } from "@/lib/api/client";
import { apiEndpoints } from "@/lib/api/endpoints";
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
  return apiFetch<SystemHealth>(toUniformaProxy(apiEndpoints.adminIntelligenceSummary));
}

export function fetchDataQuality(): Promise<DataQualityResponse> {
  return apiFetch<DataQualityResponse>(toUniformaProxy(apiEndpoints.adminIntelligenceDataQuality));
}

export function fetchSyncHealth(params: IntelligencePagination = {}): Promise<SyncHealthResponse> {
  return apiFetch<SyncHealthResponse>(toUniformaProxy(apiEndpoints.adminIntelligenceSyncHealth), {
    query: {
      page: params.page ?? 1,
      page_size: params.pageSize ?? 10
    }
  });
}

export function fetchOverrideConflicts(
  params: IntelligencePagination = {}
): Promise<OverrideConflictResponse> {
  return apiFetch<OverrideConflictResponse>(toUniformaProxy(apiEndpoints.adminIntelligenceOverrideConflicts), {
    query: {
      page: params.page ?? 1,
      page_size: params.pageSize ?? 10
    }
  });
}

function toUniformaProxy(path: string): string {
  return `/api/uniforma${path}`;
}
