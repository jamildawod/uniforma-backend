export type ProductStatus = "draft" | "active" | "archived";
export type AttributeType = "text" | "number" | "select" | "boolean";

export interface Brand {
  id: number;
  name: string;
  slug: string;
  logo_url: string | null;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  parent_id: number | null;
  position: number;
}

export interface AttributeDefinition {
  id: number;
  name: string;
  type: AttributeType;
}

export interface ProductAttributeValue {
  attribute_id: number;
  value: string;
  attribute: AttributeDefinition;
}

export interface ProductImage {
  id: number;
  variant_id: number | null;
  url: string;
  position: number;
  is_primary: boolean;
  created_at: string;
}

export interface ProductVariant {
  id: number;
  sku: string;
  ean: string | null;
  color: string | null;
  size: string | null;
  price: string | null;
  stock_quantity: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  images: ProductImage[];
}

export interface AdminProduct {
  id: string;
  external_id: string;
  name: string;
  slug: string;
  description: string | null;
  status: ProductStatus;
  brand_id: number | null;
  brand: Brand | null;
  category_id: number | null;
  category: Category | null;
  image_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
  last_seen_at?: string | null;
  images: ProductImage[];
  variants: ProductVariant[];
  attributes: ProductAttributeValue[];
  applied_overrides: Record<string, string | number | boolean | null | Record<string, unknown> | unknown[]>;
}

export interface PublicProduct {
  id: string;
  external_id: string;
  name: string;
  slug: string;
  description: string | null;
  status: ProductStatus;
  brand_id: number | null;
  brand: Brand | null;
  category_id: number | null;
  category: Category | null;
  image_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  images: ProductImage[];
  variants: ProductVariant[];
  attributes: ProductAttributeValue[];
}

export interface CatalogProductSummary {
  product_id: string;
  slug: string;
  name: string;
  created_at: string;
  category: string | null;
  brand: string | null;
  price: string | null;
  primary_image: string | null;
  colors: string[];
  sizes: string[];
}

export interface CatalogFilterOption {
  value: string;
  count: number;
}

export interface CatalogFilters {
  categories: CatalogFilterOption[];
  brands: CatalogFilterOption[];
  colors: CatalogFilterOption[];
  sizes: CatalogFilterOption[];
}

export interface CategoryTreeNode {
  id: number;
  name: string;
  slug: string;
  children: CategoryTreeNode[];
}

export interface CatalogSearchMatch {
  product_id: string;
  slug: string;
  name: string;
  category: string | null;
  primary_image: string | null;
  price: string | null;
  score: number;
}

export interface CatalogSearchResponse {
  items: CatalogSearchMatch[];
}

export interface SearchSuggestionItem {
  type: "product" | "category" | "brand";
  value: string;
  slug: string | null;
  href: string;
  product_id: string | null;
  primary_image: string | null;
  subtitle: string | null;
}

export interface SearchSuggestionResponse {
  items: SearchSuggestionItem[];
}

export interface CatalogProductList {
  products: CatalogProductSummary[];
  next_cursor: string | null;
  filters: CatalogFilters;
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
  url: string;
  variant_id?: number | null;
  is_primary?: boolean;
  position?: number;
}

export interface AdminVariantPayload {
  sku: string;
  ean?: string | null;
  size?: string | null;
  color?: string | null;
  price?: string | null;
  stock_quantity: number;
  is_active: boolean;
}

export interface AdminAttributeValuePayload {
  attribute_id: number;
  value: string;
}

export interface AdminOverridePayload {
  overrides: Record<string, string | number | boolean | null>;
}

export interface AdminProductUpsertPayload {
  name: string;
  slug?: string | null;
  description?: string | null;
  brand_id?: number | null;
  category_id?: number | null;
  status: ProductStatus;
  image_url?: string | null;
  is_active: boolean;
  variants?: AdminVariantPayload[];
  attributes: AdminAttributeValuePayload[];
}

export interface AdminProductPublishPayload {
  is_active: boolean;
}

export interface UploadResponse {
  filename: string;
  url: string;
}

export interface MediaItem {
  filename: string;
  url: string;
}

export interface DataQualityIssue {
  key: string;
  label: string;
  count: number;
}

export interface DataQualityPayload {
  issues: DataQualityIssue[];
}
