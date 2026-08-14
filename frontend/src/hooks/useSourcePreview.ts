import {
  useQuery,
} from "@tanstack/react-query";

import {
  sourceService,
} from "../services/source.service";


export function useSourcePreview(
  documentId?: string,
  chunkIndex?: number
) {
  return useQuery({
    queryKey: [
      "source-preview",
      documentId,
      chunkIndex,
    ],

    queryFn: () =>
      sourceService.getChunk(
        documentId!,
        chunkIndex!
      ),

    enabled:
      Boolean(documentId)
      && chunkIndex !== undefined,
  });
}