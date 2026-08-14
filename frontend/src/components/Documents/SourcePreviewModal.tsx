import {
  useEffect,
  useState,
} from "react";

import {
  Check,
  Copy,
  X,
} from "lucide-react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  useSourcePreview,
} from "../../context/SourcePreviewContext";

import {
  useSourcePreview as useChunk,
} from "../../hooks/useSourcePreview";

import Skeleton from "../common/Skeleton";


export default function SourcePreviewModal() {
  const {
    preview,
    closePreview,
  } = useSourcePreview();

  const {
    data,
    isLoading,
    error,
  } = useChunk(
    preview.source?.document_id,
    preview.source?.chunk_index
  );

  const [
    copied,
    setCopied,
  ] = useState(false);


  useEffect(() => {
    if (!preview.open) {
      return;
    }

    function handleKeyDown(
      event: KeyboardEvent
    ) {
      if (
        event.key === "Escape"
      ) {
        closePreview();
      }
    }

    window.addEventListener(
      "keydown",
      handleKeyDown
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown
      );
    };
  }, [
    preview.open,
    closePreview,
  ]);


  async function copyChunk() {
    if (!data?.text) {
      return;
    }

    await navigator
      .clipboard
      .writeText(
        data.text
      );

    setCopied(
      true
    );

    setTimeout(
      () => {
        setCopied(
          false
        );
      },
      2000
    );
  }


  if (!preview.open) {
    return null;
  }


  return (
    <div
      className="
        fixed
        inset-0
        z-50
        flex
        items-center
        justify-center
        bg-black/50
        p-4
        backdrop-blur-sm
      "
      onMouseDown={
        closePreview
      }
    >
      <div
        className="
          flex
          h-[75vh]
          w-full
          max-w-4xl
          flex-col
          overflow-hidden
          rounded-2xl
          bg-white
          shadow-2xl
        "
        onMouseDown={(
          event
        ) =>
          event.stopPropagation()
        }
      >

        {/* Header */}

        <div
          className="
            flex
            items-center
            justify-between
            border-b
            border-gray-200
            px-6
            py-4
          "
        >
          <div className="min-w-0">

            <h2
              className="
                truncate
                text-xl
                font-bold
                text-gray-900
              "
              title={
                preview.source
                  ?.filename
              }
            >
              📄{" "}
              {
                preview.source
                  ?.filename
              }
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Chunk #
              {
                preview.source
                  ?.chunk_index
              }
            </p>

          </div>


          <div className="ml-4 flex items-center gap-2">

            {data?.text && (
              <button
                type="button"
                onClick={() => {
                  void copyChunk();
                }}
                className="
                  rounded-lg
                  border
                  border-gray-300
                  p-2
                  transition
                  hover:bg-gray-100
                "
                title="Copy chunk"
              >
                {copied ? (
                  <Check
                    size={18}
                    className="text-green-600"
                  />
                ) : (
                  <Copy
                    size={18}
                  />
                )}
              </button>
            )}


            <button
              type="button"
              onClick={
                closePreview
              }
              className="
                rounded-lg
                border
                border-gray-300
                p-2
                transition
                hover:bg-red-50
                hover:text-red-600
              "
              title="Close"
            >
              <X
                size={20}
              />
            </button>

          </div>
        </div>


        {/* Body */}

        <div className="flex-1 overflow-y-auto p-6">

          {isLoading && (
            <div className="space-y-4">

              <Skeleton className="h-8 w-1/3" />

              <Skeleton className="h-5 w-full" />

              <Skeleton className="h-5 w-full" />

              <Skeleton className="h-5 w-5/6" />

              <Skeleton className="h-5 w-full" />

              <Skeleton className="h-5 w-2/3" />

              <Skeleton className="h-5 w-full" />

              <Skeleton className="h-5 w-4/5" />

            </div>
          )}


          {error && (
            <div
              className="
                rounded-xl
                border
                border-red-300
                bg-red-50
                p-5
                text-sm
                text-red-600
              "
            >
              Failed to load the document preview.
            </div>
          )}


          {data && (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[
                  remarkGfm,
                ]}
              >
                {data.text}
              </ReactMarkdown>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}