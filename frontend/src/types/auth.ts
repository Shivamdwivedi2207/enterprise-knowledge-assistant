export interface LoginRequest {
  email: string;
  password: string;
}


export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}


export interface TokenResponse {
  access_token: string;
  token_type: string;
}


export interface CurrentUser {
  id: string;
  full_name: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
}