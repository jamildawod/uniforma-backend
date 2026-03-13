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
