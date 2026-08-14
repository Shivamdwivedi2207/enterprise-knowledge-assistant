import api from "../api/axios";
import { API_ENDPOINTS } from "../api/endpoints";

import type {
  DocumentResponse,
  UploadResponse,
} from "../types/document";

export const documentService = {
  async getDocuments(): Promise<DocumentResponse[]> {
    const response = await api.get<DocumentResponse[]>(
      API_ENDPOINTS.DOCUMENTS
    );

    return response.data;
  },

  async upload(file: File): Promise<UploadResponse> {
    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post<UploadResponse>(
      API_ENDPOINTS.DOCUMENT_UPLOAD,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  },

  async delete(documentId: string) {
    await api.delete(
      `${API_ENDPOINTS.DOCUMENTS}/${documentId}`
    );
  },
};