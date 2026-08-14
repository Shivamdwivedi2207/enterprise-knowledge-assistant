import {
  useRef,
  useState,
} from "react";

import {
  RotateCcw,
  Send,
  Square,
} from "lucide-react";

import {
  useQueryClient,
} from "@tanstack/react-query";

import {
  useChat,
} from "../../context/ChatContext";

import {
  streamChat,
} from "../../services/stream.service";

import type {
  Source,
} from "../../types/chat";


export default function ChatInput() {
  const queryClient =
    useQueryClient();

  const [
    question,
    setQuestion,
  ] = useState("");

  const [
    streaming,
    setStreaming,
  ] = useState(false);

  const controller =
    useRef<AbortController | null>(
      null
    );

  const {
    addMessage,
    updateLastAssistantMessage,
    finishLastAssistantMessage,
    lastQuestion,
    setLastQuestion,
  } = useChat();


  async function refreshChatHistory() {
    await queryClient.invalidateQueries({
      queryKey: [
        "chat-history",
      ],
    });
  }


  async function sendQuestion(
    userQuestion: string
  ) {
    const trimmedQuestion =
      userQuestion.trim();

    if (
      !trimmedQuestion
      || streaming
    ) {
      return;
    }

    setLastQuestion(
      trimmedQuestion
    );

    addMessage({
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedQuestion,
    });

    addMessage({
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
      loading: true,
      sources: [],
    });

    let fullResponse = "";

    let latestSources:
      Source[] = [];

    setStreaming(
      true
    );

    controller.current =
      new AbortController();

    try {
      await streamChat(
        trimmedQuestion,

        {
          onChunk(chunk) {
            fullResponse +=
              chunk;

            updateLastAssistantMessage(
              fullResponse,
              undefined,
              true
            );
          },


          onSources(sources) {
            latestSources =
              sources;

            updateLastAssistantMessage(
              fullResponse,
              sources,
              true
            );
          },


          onDone() {
            finishLastAssistantMessage(
              latestSources
            );

            setStreaming(
              false
            );

            void refreshChatHistory();
          },


          onError(message) {
            const finalMessage =
              fullResponse
                ? (
                  fullResponse
                  + "\n\n"
                  + `⚠️ ${message}`
                )
                : (
                  `❌ ${message}`
                );

            updateLastAssistantMessage(
              finalMessage,
              latestSources,
              false
            );

            setStreaming(
              false
            );
          },
        },

        controller.current.signal
      );

      finishLastAssistantMessage(
        latestSources
      );

      await refreshChatHistory();

    } catch (error) {
      const aborted =
        controller.current
          ?.signal
          .aborted;

      if (aborted) {
        const stoppedMessage =
          fullResponse
            ? (
              fullResponse
              + "\n\n"
              + "⛔ Generation stopped."
            )
            : (
              "⛔ Generation stopped."
            );

        updateLastAssistantMessage(
          stoppedMessage,
          latestSources,
          false
        );
      }

      else {
        const message =
          error instanceof Error
            ? error.message
            : (
              "Failed to contact server."
            );

        updateLastAssistantMessage(
          fullResponse
            ? (
              fullResponse
              + "\n\n"
              + `❌ ${message}`
            )
            : (
              `❌ ${message}`
            ),
          latestSources,
          false
        );
      }

    } finally {
      setStreaming(
        false
      );

      controller.current =
        null;
    }
  }


  async function handleSend() {
    if (
      !question.trim()
      || streaming
    ) {
      return;
    }

    const userQuestion =
      question;

    setQuestion("");

    await sendQuestion(
      userQuestion
    );
  }


  async function regenerate() {
    if (
      !lastQuestion
      || streaming
    ) {
      return;
    }

    await sendQuestion(
      lastQuestion
    );
  }


  function stopGeneration() {
    controller.current?.abort();

    setStreaming(
      false
    );
  }


  return (
    <div className="border-t bg-white p-4">

      <div className="flex gap-3">

        <input
          className="
            flex-1
            rounded-lg
            border
            p-3
            outline-none
            focus:ring-2
            focus:ring-blue-500
            disabled:bg-gray-100
          "
          placeholder={
            streaming
              ? "Waiting for response..."
              : "Ask something or request an action..."
          }
          value={
            question
          }
          disabled={
            streaming
          }
          onChange={(event) =>
            setQuestion(
              event.target.value
            )
          }
          onKeyDown={(event) => {
            if (
              event.key === "Enter"
              && !event.shiftKey
              && !streaming
            ) {
              event.preventDefault();

              void handleSend();
            }
          }}
        />


        <button
          type="button"
          onClick={() => {
            void regenerate();
          }}
          disabled={
            streaming
            || !lastQuestion
          }
          className="
            rounded-lg
            border
            px-4
            hover:bg-gray-100
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
          title="Regenerate"
        >
          <RotateCcw
            size={18}
          />
        </button>


        {streaming ? (
          <button
            type="button"
            onClick={
              stopGeneration
            }
            className="
              rounded-lg
              bg-red-600
              px-5
              text-white
              hover:bg-red-700
            "
            title="Stop generation"
          >
            <Square
              size={18}
            />
          </button>
        ) : (
          <button
            type="button"
            onClick={() => {
              void handleSend();
            }}
            disabled={
              !question.trim()
            }
            className="
              rounded-lg
              bg-blue-600
              px-5
              text-white
              hover:bg-blue-700
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
            title="Send"
          >
            <Send
              size={20}
            />
          </button>
        )}

      </div>

    </div>
  );
}