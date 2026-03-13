export interface Category {
  id: number;
  name: string;
  slug: string;
  parent_id: number | null;
}

export interface ProductImage {
  id: number;
  variant_id: number | null;
  external_path: string;
  local_path: string | null;
  is_primary: boolean;
  sort_order: number;
}

export interface ProductVariant {
  id: number;
  sku: string;
  ean: string | null;
  color: string | null;
  size: string | null;
  price: string | null;
  currency: string | null;
  stock_quantity: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
  last_seen_at?: string | null;
  images: ProductImage[];
}

export interface SourceProductView {
  name: string | null;
  description: string | null;
  brand: string | null;
}

export interface AdminProduct {
  id: string;
  external_id: string;
  name: string;
  slug: string;
  description: string | null;
  brand: string | null;
  is_active: boolean;
  image_url: string | null;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
  last_seen_at?: string | null;
  category: Category | null;
  images: ProductImage[];
  variants: ProductVariant[];
  applied_overrides: Record<string, string | number | boolean | null | Record<string, unknown> | unknown[]>;
  source_product?: SourceProductView | null;
}

export interface PublicProduct {
  id: string;
  external_id: string;
  name: string;
  slug: string;
  description: string | null;
  brand: string | null;
  is_active: boolean;
  image_url: string | null;
  created_at: string;
  updated_at: string;
  category: Category | null;
  images: ProductImage[];
  variants: ProductVariant[];
}

export interface ProductListFilters {
  page: number;
  pageSize: number;
  search?: string;
  filter?: string;
  isActive?: "all" | "active" | "inactive";
  deleted?: "all" | "deleted" | "not_deleted";
  hasOverride?: "all" | "yes" | "no";
}

export interface AdminImagePayload {
  external_path: string;
  local_path?: string | null;
  variant_id?: number | null;
  is_primary?: boolean;
  sort_order?: number;
}

export interface AdminOverridePayload {
  overrides: Record<string, string | number | boolean | null>;
}

export interface AdminProductUpsertPayload {
  name: string;
  slug?: string | null;
  description?: string | null;
  brand?: string | null;
  category?: string | null;
  image_url?: string | null;
  is_active: boolean;
}

export interface AdminProductPublishPayload {
  is_active: boolean;
}

export interface UploadResponse {
  filename: string;
  url: string;
}
