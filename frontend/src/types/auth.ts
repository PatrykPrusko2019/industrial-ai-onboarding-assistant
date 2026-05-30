export type UserRole = "employee" | "expert" | "admin";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}


export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
}