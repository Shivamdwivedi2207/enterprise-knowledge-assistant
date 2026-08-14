import {
  useMutation,
} from "@tanstack/react-query";

import {
  chatService,
} from "../services/chat.service";


export function useAskQuestion() {
  return useMutation({
    mutationFn: (
      question: string
    ) => chatService.ask(
      question
    ),
  });
}