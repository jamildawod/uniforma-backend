export interface QuoteRequestPayload {
  name: string;
  email: string;
  company?: string | null;
  message: string;
}

export interface QuoteRequest {
  id: number;
  name: string;
  email: string;
  company: string | null;
  message: string;
  status: string;
  created_at: string;
}
