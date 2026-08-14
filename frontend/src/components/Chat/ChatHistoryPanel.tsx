import {
  History,
  LoaderCircle,
  MessageSquare,
  Plus,
} from "lucide-react";

import {
  useChatHistory,
} from "../../hooks/useChatHistory";

import {
  useChat,
} from "../../context/ChatContext";


export default function ChatHistoryPanel() {
  const {
    data,
    isLoading,
    error,
  } = useChatHistory();

  const {
    clearMessages,

    loadHistoryConversation,

    selectedHistoryId,

    setSelectedHistoryId,
  } = useChat();


  function handleNewChat() {
    clearMessages();
  }


  function openHistoryItem(
    id: string,
    question: string,
    answer: string
  ) {
    loadHistoryConversation(
      question,
      answer
    );

    setSelectedHistoryId(
      id
    );
  }


  return (
    <div className="border-t border-gray-200">

      {/* Header */}

      <div className="flex items-center justify-between px-4 py-3">

        <div className="flex items-center gap-2">

          <History
            size={17}
            className="text-gray-500"
          />

          <h3 className="text-sm font-semibold text-gray-800">
            Chat History
          </h3>

        </div>


        <button
          type="button"
          onClick={
            handleNewChat
          }
          className="
            flex
            items-center
            gap-1
            rounded-lg
            border
            border-gray-200
            px-2
            py-1
            text-xs
            font-medium
            text-gray-700
            transition
            hover:bg-gray-100
          "
          title="New Chat"
        >
          <Plus
            size={14}
          />

          New
        </button>

      </div>


      {/* Loading */}

      {isLoading && (
        <div className="flex items-center gap-2 px-4 pb-4 text-sm text-gray-500">

          <LoaderCircle
            size={16}
            className="animate-spin"
          />

          Loading history...

        </div>
      )}


      {/* Error */}

      {error && (
        <div className="px-4 pb-4 text-sm text-red-600">
          Failed to load chat history.
        </div>
      )}


      {/* Empty */}

      {!isLoading
        && !error
        && !data?.length
        && (
          <div className="px-4 pb-4 text-sm text-gray-500">
            No previous chats.
          </div>
        )}


      {/* History List */}

      {data
        && data.length > 0
        && (
          <div
            className="
              max-h-64
              space-y-1
              overflow-y-auto
              px-2
              pb-3
            "
          >

            {data.map(
              (item) => {
                const selected =
                  selectedHistoryId
                  === item.id;

                return (
                  <button
                    key={
                      item.id
                    }
                    type="button"
                    onClick={() =>
                      openHistoryItem(
                        item.id,
                        item.question,
                        item.answer
                      )
                    }
                    className={`
                      flex
                      w-full
                      items-start
                      gap-2
                      rounded-lg
                      px-3
                      py-2
                      text-left
                      transition
                      ${
                        selected
                          ? (
                            "bg-blue-50 "
                            + "text-blue-700"
                          )
                          : (
                            "hover:bg-gray-100"
                          )
                      }
                    `}
                  >

                    <MessageSquare
                      size={15}
                      className={
                        selected
                          ? (
                            "mt-0.5 "
                            + "shrink-0 "
                            + "text-blue-500"
                          )
                          : (
                            "mt-0.5 "
                            + "shrink-0 "
                            + "text-gray-400"
                          )
                      }
                    />


                    <div className="min-w-0">

                      <p
                        className={`
                          truncate
                          text-sm
                          font-medium
                          ${
                            selected
                              ? "text-blue-700"
                              : "text-gray-800"
                          }
                        `}
                      >
                        {item.question}
                      </p>


                      <p
                        className={`
                          mt-1
                          text-xs
                          ${
                            selected
                              ? "text-blue-400"
                              : "text-gray-400"
                          }
                        `}
                      >
                        {new Date(
                          item.created_at
                        ).toLocaleString()}
                      </p>

                    </div>

                  </button>
                );
              }
            )}

          </div>
        )}

    </div>
  );
}