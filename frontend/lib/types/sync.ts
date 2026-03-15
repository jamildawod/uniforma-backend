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

export interface PimSyncResponse {
  products_created: number;
  products_updated: number;
  products_unchanged: number;
  variants_created: number;
  variants_updated: number;
  variants_unchanged: number;
  images_discovered: number;
  images_synced: number;
  records_processed: number;
  records_created: number;
  records_updated: number;
}
