export interface QuoteRequestPayload {
  product_id?: string | null;
  variant_id?: number | null;
  name: string;
  email: string;
  company?: string | null;
  message: string;
}

export interface QuoteRequest {
  id: number;
  product_id: string | null;
  variant_id: number | null;
  name: string;
  email: string;
  company: string | null;
  message: string;
  status: string;
  created_at: string;
}
