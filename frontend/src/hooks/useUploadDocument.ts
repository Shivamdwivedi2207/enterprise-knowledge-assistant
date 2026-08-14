import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import toast from "react-hot-toast";

import {
  documentService,
} from "../services/document.service";


export function useUploadDocument() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      file: File
    ) =>
      documentService.upload(
        file
      ),

    onSuccess: async () => {
      toast.success(
        "Document uploaded successfully"
      );

      await queryClient.invalidateQueries({
        queryKey: [
          "documents",
        ],
      });
    },

    onError: () => {
      toast.error(
        "Failed to upload document"
      );
    },
  });
}