import {
  FileText,
  LoaderCircle,
  Trash2,
} from "lucide-react";

import {
  useDocuments,
} from "../../hooks/useDocuments";

import {
  useDeleteDocument,
} from "../../hooks/useDeleteDocument";


export default function DocumentList() {
  const {
    data,
    isLoading,
    error,
  } = useDocuments();

  const deleteMutation =
    useDeleteDocument();


  function handleDelete(
    id: string,
    filename: string
  ) {
    const confirmed =
      window.confirm(
        `Delete "${filename}"?`
      );

    if (!confirmed) {
      return;
    }

    deleteMutation.mutate(
      id
    );
  }


  function formatFileSize(
    bytes: number
  ) {
    if (
      bytes < 1024
    ) {
      return `${bytes} B`;
    }

    if (
      bytes
      < 1024 * 1024
    ) {
      return (
        `${(
          bytes / 1024
        ).toFixed(2)} KB`
      );
    }

    return (
      `${(
        bytes
        / (1024 * 1024)
      ).toFixed(2)} MB`
    );
  }


  if (isLoading) {
    return (
      <div className="flex items-center gap-2 p-4 text-sm text-gray-500">
        <LoaderCircle
          size={18}
          className="animate-spin"
        />

        Loading documents...
      </div>
    );
  }


  if (error) {
    return (
      <div className="p-4 text-sm text-red-600">
        Failed to load documents.
      </div>
    );
  }


  return (
    <div className="space-y-3 p-4">

      <div className="flex items-center justify-between">

        <h2 className="text-lg font-semibold text-gray-900">
          Documents
        </h2>

        <span className="rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-600">
          {data?.length ?? 0}
        </span>

      </div>


      {!data?.length && (
        <div
          className="
            rounded-lg
            border
            border-dashed
            border-gray-300
            p-4
            text-center
            text-sm
            text-gray-500
          "
        >
          No documents uploaded.
        </div>
      )}


      {data?.map(
        (document) => (
          <div
            key={
              document.id
            }
            className="
              rounded-xl
              border
              border-gray-200
              bg-white
              p-4
              shadow-sm
              transition
              hover:shadow-md
            "
          >
            <div className="flex items-start justify-between gap-3">

              <div className="flex min-w-0 gap-3">

                <FileText
                  className="mt-1 shrink-0 text-blue-600"
                  size={20}
                />

                <div className="min-w-0">

                  <p
                    className="
                      truncate
                      font-medium
                      text-gray-900
                    "
                    title={
                      document.filename
                    }
                  >
                    {
                      document.filename
                    }
                  </p>

                  <p className="mt-1 text-xs text-gray-500">
                    {formatFileSize(
                      document.file_size
                    )}
                  </p>

                  <p className="mt-1 text-xs text-gray-400">
                    {
                      new Date(
                        document.created_at
                      ).toLocaleString()
                    }
                  </p>

                </div>

              </div>


              <button
                onClick={() =>
                  handleDelete(
                    document.id,
                    document.filename
                  )
                }
                className="
                  rounded-lg
                  p-2
                  text-red-500
                  transition
                  hover:bg-red-100
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
                disabled={
                  deleteMutation.isPending
                }
                title="Delete document"
              >
                {deleteMutation.isPending ? (
                  <LoaderCircle
                    size={18}
                    className="animate-spin"
                  />
                ) : (
                  <Trash2
                    size={18}
                  />
                )}
              </button>

            </div>
          </div>
        )
      )}

    </div>
  );
}