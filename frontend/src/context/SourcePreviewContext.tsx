import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

import type { Source } from "../types/chat";

interface PreviewState {
  open: boolean;
  source?: Source;
}

interface PreviewContextType {
  preview: PreviewState;

  openPreview: (
    source: Source
  ) => void;

  closePreview: () => void;
}

const SourcePreviewContext =
  createContext<PreviewContextType | null>(
    null
  );

export function SourcePreviewProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [preview, setPreview] =
    useState<PreviewState>({
      open: false,
    });

  function openPreview(
    source: Source
  ) {
    setPreview({
      open: true,
      source,
    });
  }

  function closePreview() {
    setPreview({
      open: false,
    });
  }

  return (
    <SourcePreviewContext.Provider
      value={{
        preview,
        openPreview,
        closePreview,
      }}
    >
      {children}
    </SourcePreviewContext.Provider>
  );
}

export function useSourcePreview() {
  const context = useContext(
    SourcePreviewContext
  );

  if (!context) {
    throw new Error(
      "useSourcePreview must be used inside SourcePreviewProvider"
    );
  }

  return context;
}