export type Severity = "healthy" | "warning" | "critical" | "unavailable";

export interface SystemHealth {
  status: Severity;
  generated_at: string;
  total_products: number;
  active_products: number;
  deleted_products: number;
  total_variants: number;
  last_successful_sync_at: string | null;
  running_syncs: number;
  override_count: number;
}

export interface DataQualityMetric {
  key: string;
  label: string;
  count: number;
  description: string;
  filter: string;
  severity: Severity;
}

export interface SyncRun {
  id: number;
  started_at: string;
  finished_at: string | null;
  products_created: number;
  products_updated: number;
  variants_created: number;
  variants_updated: number;
  images_synced: number;
  status: "success" | "failed" | "running";
  error_message: string | null;
}

export interface SyncHealthResponse {
  status: Severity;
  generated_at: string;
  running_syncs: number;
  last_successful_sync_at: string | null;
  failed_runs_last_24h: number;
  average_duration_seconds?: number | null;
  last_failed_sync_at?: string | null;
  soft_deleted_products_last_run?: number;
  soft_deleted_variants_last_run?: number;
  recent_runs: SyncRun[];
  page: number;
  page_size: number;
  total: number;
}

export interface OverrideConflict {
  id: string;
  product_id: string;
  product_name: string;
  field_name: string;
  source_value: string | null;
  override_value: string | null;
  final_value: string | null;
  severity: Severity;
  updated_at: string;
}

export interface OverrideConflictResponse {
  status?: Severity;
  generated_at?: string;
  page: number;
  page_size: number;
  total: number;
  conflicts: OverrideConflict[];
}

export interface DataQualityResponse {
  status?: Severity;
  generated_at: string;
  metrics: DataQualityMetric[];
}
