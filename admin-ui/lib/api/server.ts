import { cookies } from "next/headers";

import { AUTH_COOKIE } from "@/lib/auth/cookies";
import { env } from "@/lib/config/env";
import type { SyncRun } from "@/lib/types/sync";
import type {
  AdminProduct,
  AttributeDefinition,
  Brand,
  Category,
  DataQualityPayload,
  MediaItem,
  ProductListFilters,
  PublicProduct
} from "@/lib/types/products";
import type { QuoteRequest } from "@/lib/types/quotes";
import type { SystemHealth } from "@/types/intelligence";

export async function fetchAdminProducts(filters: ProductListFilters): Promise<AdminProduct[]> {
  const products = await fetchWithToken<AdminProduct[]>(
    `/api/v1/admin/products?limit=${filters.pageSize}&offset=${(filters.page - 1) * filters.pageSize}`
  );

  return applyProductFilters(products, filters);
}

export async function fetchAdminProduct(id: string): Promise<AdminProduct | null> {
  try {
    return await fetchWithToken<AdminProduct>(`/api/v1/admin/products/${id}`);
  } catch {
    return null;
  }
}

export async function fetchAdminBrands(): Promise<Brand[]> {
  try {
    return await fetchWithToken<Brand[]>("/api/v1/admin/brands");
  } catch {
    return [];
  }
}

export async function fetchAdminCategories(): Promise<Category[]> {
  try {
    return await fetchWithToken<Category[]>("/api/v1/admin/categories");
  } catch {
    return [];
  }
}

export async function fetchAdminAttributes(): Promise<AttributeDefinition[]> {
  try {
    return await fetchWithToken<AttributeDefinition[]>("/api/v1/admin/attributes");
  } catch {
    return [];
  }
}

export async function fetchAdminMedia(): Promise<MediaItem[]> {
  try {
    return await fetchWithToken<MediaItem[]>("/api/v1/admin/media");
  } catch {
    return [];
  }
}

export async function fetchAdminQuotes(): Promise<QuoteRequest[]> {
  try {
    return await fetchWithToken<QuoteRequest[]>("/api/v1/admin/quotes");
  } catch {
    return [];
  }
}

export async function fetchAdminDataQuality(): Promise<DataQualityPayload | null> {
  try {
    return await fetchWithToken<DataQualityPayload>("/api/v1/admin/data-quality");
  } catch {
    return null;
  }
}

export async function fetchSyncRuns(): Promise<SyncRun[]> {
  try {
    return await fetchWithToken<SyncRun[]>("/api/v1/admin/sync/runs");
  } catch {
    return [];
  }
}

export async function fetchSystemHealthSummary(): Promise<SystemHealth | null> {
  try {
    return await fetchWithToken<SystemHealth>("/api/v1/admin/intelligence/summary");
  } catch {
    return null;
  }
}

export async function fetchPublicProducts(): Promise<PublicProduct[]> {
  try {
    return await fetchWithoutToken<PublicProduct[]>("/api/v1/products");
  } catch {
    return [];
  }
}

export async function fetchPublicProduct(slug: string): Promise<PublicProduct | null> {
  try {
    return await fetchWithoutToken<PublicProduct>(`/api/v1/products/${slug}`);
  } catch {
    return null;
  }
}

export async function fetchWithToken<T>(path: string): Promise<T> {
  const token = cookies().get(AUTH_COOKIE)?.value;
  const response = await fetch(`${env.UNIFORMA_API_BASE_URL}${path}`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}`);
  }

  return (await response.json()) as T;
}

async function fetchWithoutToken<T>(path: string): Promise<T> {
  const response = await fetch(`${env.UNIFORMA_API_BASE_URL}${path}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}`);
  }

  return (await response.json()) as T;
}

function applyProductFilters(products: AdminProduct[], filters: ProductListFilters): AdminProduct[] {
  return products.filter((product) => {
    const filterKey = filters.filter;
    const matchesSearch =
      !filters.search ||
      product.name.toLowerCase().includes(filters.search.toLowerCase()) ||
      product.variants.some((variant) => variant.sku.toLowerCase().includes(filters.search!.toLowerCase()));

    const matchesIsActive =
      filters.isActive === undefined ||
      filters.isActive === "all" ||
      (filters.isActive === "active" ? product.is_active : !product.is_active);

    const isDeleted = Boolean(product.deleted_at);
    const matchesDeleted =
      filters.deleted === undefined ||
      filters.deleted === "all" ||
      (filters.deleted === "deleted" ? isDeleted : !isDeleted);

    const hasOverride = Object.keys(product.applied_overrides ?? {}).length > 0;
    const matchesOverride =
      filters.hasOverride === undefined ||
      filters.hasOverride === "all" ||
      (filters.hasOverride === "yes" ? hasOverride : !hasOverride);

    const matchesMetricFilter =
      !filterKey ||
      (filterKey === "missing_brand" && !product.brand) ||
      (filterKey === "missing_description" && !product.description) ||
      (filterKey === "variants_missing_ean" && product.variants.some((variant) => !variant.ean));

    return matchesSearch && matchesIsActive && matchesDeleted && matchesOverride && matchesMetricFilter;
  });
}
