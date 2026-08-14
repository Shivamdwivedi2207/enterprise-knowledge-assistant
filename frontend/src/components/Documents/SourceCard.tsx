import {
  FileText,
} from "lucide-react";

import type {
  Source,
} from "../../types/chat";

import {
  useSourcePreview,
} from "../../context/SourcePreviewContext";


interface Props {
  source: Source;
}


export default function SourceCard({
  source,
}: Props) {
  const {
    openPreview,
  } = useSourcePreview();

  return (
    <button
      type="button"
      onClick={() =>
        openPreview(
          source
        )
      }
      className="
        w-full
        rounded-lg
        border
        border-gray-200
        bg-gray-50
        p-3
        text-left
        transition
        hover:border-blue-500
        hover:bg-blue-50
      "
    >
      <div className="flex items-center gap-3">

        <FileText
          size={20}
          className="shrink-0 text-blue-600"
        />

        <div className="min-w-0">

          <div
            className="
              truncate
              font-medium
              text-gray-900
            "
            title={
              source.filename
            }
          >
            {source.filename}
          </div>

          <div className="mt-1 text-xs text-gray-500">
            Chunk #{source.chunk_index}
          </div>

        </div>

      </div>
    </button>
  );
}