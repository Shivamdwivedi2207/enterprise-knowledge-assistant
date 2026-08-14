import {
  useQuery,
} from "@tanstack/react-query";

import {
  documentService,
} from "../services/document.service";


export function useDocuments() {
  return useQuery({
    queryKey: [
      "documents",
    ],

    queryFn: () =>
      documentService.getDocuments(),
  });
}