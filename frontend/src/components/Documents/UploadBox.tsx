import type {
  ChangeEvent,
} from "react";

import {
  FileUp,
  LoaderCircle,
} from "lucide-react";

import {
  useUploadDocument,
} from "../../hooks/useUploadDocument";


export default function UploadBox() {
  const uploadMutation =
    useUploadDocument();


  function handleFileChange(
    e: ChangeEvent<HTMLInputElement>
  ) {
    const file =
      e.target.files?.[0];

    if (!file) {
      return;
    }

    const isPdf =
      file.type === "application/pdf"
      || file.name
        .toLowerCase()
        .endsWith(".pdf");

    if (!isPdf) {
      window.alert(
        "Please select a PDF file."
      );

      e.target.value = "";

      return;
    }

    uploadMutation.mutate(
      file
    );

    e.target.value = "";
  }


  return (
    <div
      className="
        rounded-xl
        border
        border-dashed
        border-gray-300
        bg-gray-50
        p-6
        text-center
      "
    >
      <div className="mb-3 flex justify-center">
        <FileUp
          size={28}
          className="text-blue-600"
        />
      </div>

      <p className="mb-4 text-sm text-gray-600">
        Upload a PDF to add it to your knowledge base.
      </p>

      <label
        htmlFor="pdf-upload"
        className={`
          inline-flex
          items-center
          justify-center
          rounded-lg
          px-5
          py-2
          font-medium
          text-white
          transition
          ${
            uploadMutation.isPending
              ? (
                "cursor-not-allowed "
                + "bg-blue-400"
              )
              : (
                "cursor-pointer "
                + "bg-blue-600 "
                + "hover:bg-blue-700"
              )
          }
        `}
      >
        {uploadMutation.isPending ? (
          <>
            <LoaderCircle
              size={18}
              className="mr-2 animate-spin"
            />
            Uploading...
          </>
        ) : (
          "Upload PDF"
        )}
      </label>

      <input
        id="pdf-upload"
        type="file"
        accept=".pdf,application/pdf"
        className="hidden"
        disabled={
          uploadMutation.isPending
        }
        onChange={
          handleFileChange
        }
      />

      {uploadMutation.isError && (
        <p className="mt-4 text-sm text-red-600">
          Failed to upload document.
        </p>
      )}

      {uploadMutation.isSuccess && (
        <p className="mt-4 text-sm text-green-600">
          Document uploaded successfully.
        </p>
      )}
    </div>
  );
}