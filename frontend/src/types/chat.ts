export interface Source {
  filename: string;
  chunk_index: number;
  document_id: string;
}


export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  loading?: boolean;
  sources?: Source[];
}


export interface ChatRequest {
  question: string;
}


export interface ChatResponse {
  answer: string;
  sources: Source[];
}


export interface ChatHistoryItem {
  id: string;
  question: string;
  answer: string;
  created_at: string;
}