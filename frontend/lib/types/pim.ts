export type PimSourceType = "ftp" | "sftp" | "http" | "local";

export interface PimSource {
  id: number;
  name: string;
  type: PimSourceType;
  host: string | null;
  port: number | null;
  username: string | null;
  password: string | null;
  path: string | null;
  file_pattern: string | null;
  schedule: string | null;
  is_active: boolean;
  created_at: string;
}

export interface PimSourcePayload {
  name: string;
  type: PimSourceType;
  host?: string | null;
  port?: number | null;
  username?: string | null;
  password?: string | null;
  path?: string | null;
  file_pattern?: string | null;
  schedule?: string | null;
  is_active?: boolean;
}

export interface PimImportRun {
  id: number;
  source_id: number | null;
  status: string;
  started_at: string;
  finished_at: string | null;
  records_processed: number;
  records_created: number;
  records_updated: number;
  error_log: string | null;
  source: PimSource | null;
}

export interface PimConnectionTestResponse {
  ok: boolean;
}

export interface HejcoIntegrationSetting {
  provider: string;
  ftp_host: string | null;
  ftp_username: string | null;
  ftp_password_masked: string | null;
  has_password: boolean;
  pictures_path: string;
  product_data_path: string;
  stock_path: string;
  sync_enabled: boolean;
  sync_hour: number;
  timeout_seconds: number;
  last_sync_at: string | null;
  last_sync_status: string | null;
  last_sync_message: string | null;
  last_imported_product_count: number | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface HejcoIntegrationPayload {
  provider?: string;
  ftp_host: string;
  ftp_username?: string | null;
  ftp_password?: string | null;
  pictures_path: string;
  product_data_path: string;
  stock_path: string;
  sync_enabled: boolean;
  sync_hour: number;
  timeout_seconds: number;
}

export interface HejcoConnectionTestResult {
  ok: boolean;
  message: string;
}

export interface HejcoSyncResult {
  products_imported: number;
  products_updated: number;
  images_matched: number;
  stock_updated: number;
  variants_imported: number;
  variants_updated: number;
  message: string | null;
}
