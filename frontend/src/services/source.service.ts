import api from "../api/axios";

import {
  API_ENDPOINTS,
} from "../api/endpoints";

import type {
  SourcePreview,
} from "../types/source";


export const sourceService = {
  async getChunk(
    documentId: string,
    chunkIndex: number
  ): Promise<SourcePreview> {
    const response =
      await api.get<SourcePreview>(
        `${API_ENDPOINTS.SOURCE_PREVIEW}/${documentId}/${chunkIndex}`
      );

    return response.data;
  },
};