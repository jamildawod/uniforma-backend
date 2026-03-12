import type { AdminImagePayload, AdminOverridePayload, AdminProduct, ProductListFilters } from "@/lib/types/products";
import type { AuthTokens } from "@/lib/types/auth";
import type { PimSyncResponse, SyncRun } from "@/lib/types/sync";

type RequestOptions = RequestInit & {
  query?: Record<string, string | number | undefined>;
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = new URL(path, "http://localhost");
  if (options.query) {
    for (const [key, value] of Object.entries(options.query)) {
      if (value !== undefined && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  const response = await fetch(url.pathname + url.search, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    },
    credentials: "include",
    cache: "no-store"
  });

  if (!response.ok) {
    const errorPayload = (await safeJson(response)) as { detail?: string } | null;
    throw new ApiError(errorPayload?.detail ?? "Request failed", response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function loginRequest(payload: { email: string; password: string }): Promise<AuthTokens> {
  return apiFetch<AuthTokens>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function logoutRequest(): Promise<void> {
  return apiFetch<void>("/api/auth/logout", {
    method: "POST"
  });
}

export function patchProductOverride(productId: string, payload: AdminOverridePayload): Promise<AdminProduct> {
  return apiFetch<AdminProduct>(`/api/uniforma/api/v1/admin/products/${productId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function createProductImage(productId: string, payload: AdminImagePayload): Promise<AdminProduct> {
  return apiFetch<AdminProduct>(`/api/uniforma/api/v1/admin/products/${productId}/image`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function triggerPimSync(): Promise<PimSyncResponse> {
  return apiFetch<PimSyncResponse>("/api/uniforma/api/v1/admin/sync/pim", {
    method: "POST"
  });
}

export function getSyncRuns(): Promise<SyncRun[]> {
  return apiFetch<SyncRun[]>("/api/uniforma/api/v1/admin/sync/runs");
}

export function getAdminProduct(productId: string): Promise<AdminProduct> {
  return apiFetch<AdminProduct>(`/api/uniforma/api/v1/admin/products/${productId}`);
}

export function getAdminProducts(filters: ProductListFilters): Promise<AdminProduct[]> {
  return apiFetch<AdminProduct[]>("/api/uniforma/api/v1/admin/products", {
    query: {
      limit: filters.pageSize,
      offset: (filters.page - 1) * filters.pageSize
    }
  });
}

async function safeJson(response: Response): Promise<unknown | null> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}
