import api from "../api/axios";

import {
  API_ENDPOINTS,
} from "../api/endpoints";

import type {
  ChatHistoryItem,
  ChatRequest,
  ChatResponse,
} from "../types/chat";


export const chatService = {
  async ask(
    question: string
  ): Promise<ChatResponse> {
    const body: ChatRequest = {
      question,
    };

    const response =
      await api.post<ChatResponse>(
        API_ENDPOINTS.CHAT,
        body
      );

    return response.data;
  },


  async getHistory(): Promise<
    ChatHistoryItem[]
  > {
    const response =
      await api.get<ChatHistoryItem[]>(
        API_ENDPOINTS.CHAT_HISTORY
      );

    return response.data;
  },
};