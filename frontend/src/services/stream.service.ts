import {
  API_BASE_URL,
} from "../api/axios";

import {
  API_ENDPOINTS,
} from "../api/endpoints";

import type {
  Source,
} from "../types/chat";


interface StreamCallbacks {
  onChunk: (chunk: string) => void;

  onSources: (
    sources: Source[]
  ) => void;

  onDone?: () => void;

  onError?: (
    message: string
  ) => void;
}


interface ChunkEventData {
  content?: string;
}


interface ErrorEventData {
  message?: string;
}


export async function streamChat(
  question: string,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const token = localStorage.getItem(
    "access_token"
  );

  if (!token) {
    const message =
      "Your session has expired. Please log in again.";

    callbacks.onError?.(
      message
    );

    throw new Error(
      message
    );
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}${API_ENDPOINTS.STREAM_CHAT}`,
      {
        method: "POST",

        headers: {
          Authorization:
            `Bearer ${token}`,

          "Content-Type":
            "application/json",
        },

        body: JSON.stringify({
          question,
        }),

        signal,
      }
    );

    if (!response.ok) {
      let message =
        "Unable to complete the request.";

      try {
        const errorData =
          await response.json();

        if (
          typeof errorData?.detail
          === "string"
        ) {
          message =
            errorData.detail;
        }

        else if (
          typeof errorData?.message
          === "string"
        ) {
          message =
            errorData.message;
        }
      }

      catch {
        const text =
          await response.text();

        if (text) {
          message = text;
        }
      }

      callbacks.onError?.(
        message
      );

      throw new Error(
        message
      );
    }

    if (!response.body) {
      const message =
        "Streaming response is not available.";

      callbacks.onError?.(
        message
      );

      throw new Error(
        message
      );
    }

    const reader =
      response.body.getReader();

    const decoder =
      new TextDecoder();

    let buffer = "";

    const processEvent = (
      eventBlock: string
    ) => {
      if (!eventBlock.trim()) {
        return;
      }

      const lines =
        eventBlock.split("\n");

      let eventName = "";

      const dataLines:
        string[] = [];

      for (const line of lines) {
        if (
          line.startsWith(
            "event:"
          )
        ) {
          eventName =
            line
              .slice(
                "event:".length
              )
              .trim();
        }

        else if (
          line.startsWith(
            "data:"
          )
        ) {
          dataLines.push(
            line
              .slice(
                "data:".length
              )
              .trim()
          );
        }
      }

      const data =
        dataLines.join("\n");

      if (!eventName) {
        return;
      }

      try {
        if (
          eventName ===
          "chunk"
        ) {
          const parsed =
            JSON.parse(
              data
            ) as ChunkEventData;

          if (
            parsed.content
          ) {
            callbacks.onChunk(
              parsed.content
            );
          }

          return;
        }

        if (
          eventName ===
          "sources"
        ) {
          const parsed =
            JSON.parse(
              data || "[]"
            ) as Source[];

          callbacks.onSources(
            Array.isArray(parsed)
              ? parsed
              : []
          );

          return;
        }

        if (
          eventName ===
          "done"
        ) {
          callbacks.onDone?.();

          return;
        }

        if (
          eventName ===
          "error"
        ) {
          const parsed =
            JSON.parse(
              data || "{}"
            ) as ErrorEventData;

          callbacks.onError?.(
            parsed.message
              || "Unable to complete the request."
          );

          return;
        }
      }

      catch {
        callbacks.onError?.(
          "Unable to process the server response."
        );
      }
    };

    while (true) {
      const {
        value,
        done,
      } =
        await reader.read();

      if (done) {
        break;
      }

      buffer +=
        decoder.decode(
          value,
          {
            stream: true,
          }
        );

      const events =
        buffer.split(
          "\n\n"
        );

      buffer =
        events.pop()
        ?? "";

      for (
        const event
        of events
      ) {
        processEvent(
          event
        );
      }
    }

    buffer +=
      decoder.decode();

    if (
      buffer.trim()
    ) {
      processEvent(
        buffer
      );
    }
  }

  catch (error) {
    if (
      error
      instanceof DOMException
      && error.name
      === "AbortError"
    ) {
      return;
    }

    const message =
      error
      instanceof Error
        ? error.message
        : (
          "Unable to complete "
          + "the request."
        );

    callbacks.onError?.(
      message
    );

    throw error;
  }
}