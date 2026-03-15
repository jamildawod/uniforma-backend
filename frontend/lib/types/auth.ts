export type UserRole = "admin" | "editor";

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
}

export interface SessionUser {
  email: string | null;
  role: UserRole;
}

export interface SessionState {
  isAuthenticated: boolean;
  user: SessionUser | null;
}
