export const API_ENDPOINTS = {
  LOGIN: "/auth/login",
  REGISTER: "/auth/register",
  ME: "/users/me",

  DOCUMENT_UPLOAD: "/documents/upload",
  DOCUMENTS: "/documents",

  CHAT: "/chat",
  STREAM_CHAT: "/chat/stream",
  CHAT_HISTORY: "/chat/history",

  SOURCE_PREVIEW: "/sources",

  ADMIN_USERS: "/admin/users",
} as const;