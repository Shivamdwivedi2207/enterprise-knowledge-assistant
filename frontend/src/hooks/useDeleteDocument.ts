import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import toast from "react-hot-toast";

import {
  documentService,
} from "../services/document.service";


export function useDeleteDocument() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      documentId: string
    ) =>
      documentService.delete(
        documentId
      ),

    onSuccess: async () => {
      toast.success(
        "Document deleted successfully"
      );

      await queryClient.invalidateQueries({
        queryKey: [
          "documents",
        ],
      });
    },

    onError: () => {
      toast.error(
        "Failed to delete document"
      );
    },
  });
}