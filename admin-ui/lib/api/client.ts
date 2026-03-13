import type {
  AdminImagePayload,
  AdminOverridePayload,
  AdminProduct,
  AdminProductPublishPayload,
  AdminProductUpsertPayload,
  ProductListFilters,
  PublicProduct,
  UploadResponse
} from "@/lib/types/products";
import type { AuthTokens } from "@/lib/types/auth";
import type { QuoteRequest, QuoteRequestPayload } from "@/lib/types/quotes";
import type { PimSyncResponse, SyncRun } from "@/lib/types/sync";
import { apiEndpoints } from "@/lib/api/endpoints";

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

  const headers = new Headers(options.headers ?? {});
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url.pathname + url.search, {
    ...options,
    headers,
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
  const form = new URLSearchParams({
    username: payload.email,
    password: payload.password
  });

  return apiFetch<AuthTokens>("/api/v1/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: form.toString()
  });
}

export function logoutRequest(): Promise<void> {
  return apiFetch<void>("/api/auth/logout", {
    method: "POST"
  });
}

export function patchProductOverride(productId: string, payload: AdminOverridePayload): Promise<AdminProduct> {
  return apiFetch<AdminProduct>(toUniformaProxy(apiEndpoints.adminProduct(productId)), {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function createAdminProduct(payload: AdminProductUpsertPayload): Promise<AdminProduct> {
  return apiFetch<AdminProduct>(toUniformaProxy(apiEndpoints.adminProducts), {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateAdminProduct(productId: string, payload: AdminProductUpsertPayload): Promise<AdminProduct> {
  return apiFetch<AdminProduct>(toUniformaProxy(apiEndpoints.adminProduct(productId)), {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export function deleteAdminProduct(productId: string): Promise<void> {
  return apiFetch<void>(toUniformaProxy(apiEndpoints.adminProduct(productId)), {
    method: "DELETE"
  });
}

export function publishAdminProduct(productId: string, payload: AdminProductPublishPayload): Promise<AdminProduct> {
  return apiFetch<AdminProduct>(toUniformaProxy(apiEndpoints.adminProductPublish(productId)), {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function createProductImage(productId: string, payload: AdminImagePayload): Promise<AdminProduct> {
  return apiFetch<AdminProduct>(toUniformaProxy(apiEndpoints.adminProductImage(productId)), {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function uploadAdminImage(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.set("file", file);
  return apiFetch<UploadResponse>(toUniformaProxy(apiEndpoints.adminUpload), {
    method: "POST",
    body: formData
  });
}

export function triggerPimSync(): Promise<PimSyncResponse> {
  return apiFetch<PimSyncResponse>(toUniformaProxy(apiEndpoints.adminSyncTrigger), {
    method: "POST"
  });
}

export function getSyncRuns(): Promise<SyncRun[]> {
  return apiFetch<SyncRun[]>(toUniformaProxy(apiEndpoints.adminSyncRuns));
}

export function getAdminProduct(productId: string): Promise<AdminProduct> {
  return apiFetch<AdminProduct>(toUniformaProxy(apiEndpoints.adminProduct(productId)));
}

export function getAdminProducts(filters: ProductListFilters): Promise<AdminProduct[]> {
  return apiFetch<AdminProduct[]>(toUniformaProxy(apiEndpoints.adminProducts), {
    query: {
      limit: filters.pageSize,
      offset: (filters.page - 1) * filters.pageSize
    }
  });
}

export function getAdminQuotes(): Promise<QuoteRequest[]> {
  return apiFetch<QuoteRequest[]>(toUniformaProxy(apiEndpoints.adminQuotes));
}

export function getPublicProducts(): Promise<PublicProduct[]> {
  return apiFetch<PublicProduct[]>(apiEndpoints.publicProducts);
}

export function getPublicProduct(slug: string): Promise<PublicProduct> {
  return apiFetch<PublicProduct>(apiEndpoints.publicProduct(slug));
}

export function createQuoteRequest(payload: QuoteRequestPayload): Promise<QuoteRequest> {
  return apiFetch<QuoteRequest>(apiEndpoints.quotes, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

async function safeJson(response: Response): Promise<unknown | null> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function toUniformaProxy(path: string): string {
  return `/api/uniforma${path}`;
}
