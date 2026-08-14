import {
  useQuery,
} from "@tanstack/react-query";

import {
  chatService,
} from "../services/chat.service";


export function useChatHistory() {
  return useQuery({
    queryKey: [
      "chat-history",
    ],

    queryFn: () =>
      chatService.getHistory(),

    staleTime:
      30 * 1000,
  });
}