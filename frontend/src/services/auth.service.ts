import api from "../api/axios";
import { API_ENDPOINTS } from "../api/endpoints";

import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
} from "../types/auth";

export const authService = {
  async register(data: RegisterRequest) {
    const response = await api.post(
      API_ENDPOINTS.REGISTER,
      data
    );

    return response.data;
  },

  async login(
    data: LoginRequest
  ): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>(
      API_ENDPOINTS.LOGIN,
      data
    );

    return response.data;
  },

  async me() {
    const response = await api.get(
      API_ENDPOINTS.ME
    );

    return response.data;
  },

  saveToken(token: string) {
    localStorage.setItem(
      "access_token",
      token
    );
  },

  getToken() {
    return localStorage.getItem(
      "access_token"
    );
  },

  logout() {
    localStorage.removeItem(
      "access_token"
    );
  },

  isAuthenticated() {
    return !!this.getToken();
  },
};