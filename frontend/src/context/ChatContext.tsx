import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

import type {
  ChatMessage,
  Source,
} from "../types/chat";


interface ChatContextType {
  messages: ChatMessage[];

  addMessage: (
    message: ChatMessage
  ) => void;

  updateLastAssistantMessage: (
    text: string,
    sources?: Source[],
    loading?: boolean
  ) => void;

  finishLastAssistantMessage: (
    sources?: Source[]
  ) => void;

  clearMessages: () => void;

  loadHistoryConversation: (
    question: string,
    answer: string
  ) => void;

  selectedHistoryId: string | null;

  setSelectedHistoryId: (
    id: string | null
  ) => void;

  lastQuestion: string;

  setLastQuestion: (
    question: string
  ) => void;
}


const ChatContext =
  createContext<ChatContextType | null>(
    null
  );


function createWelcomeMessage(): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role: "assistant",
    content:
      "👋 Hello! Upload your documents and ask me anything.",
    loading: false,
    sources: [],
  };
}


export function ChatProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [
    messages,
    setMessages,
  ] = useState<ChatMessage[]>([
    createWelcomeMessage(),
  ]);

  const [
    lastQuestion,
    setLastQuestion,
  ] = useState("");

  const [
    selectedHistoryId,
    setSelectedHistoryId,
  ] = useState<string | null>(
    null
  );


  function addMessage(
    message: ChatMessage
  ) {
    setMessages(
      (prev) => [
        ...prev,
        message,
      ]
    );

    // Once a new message is added, the user is no longer
    // simply viewing an old history item.
    setSelectedHistoryId(
      null
    );
  }


  function updateLastAssistantMessage(
    text: string,
    sources?: Source[],
    loading = true
  ) {
    setMessages((prev) => {
      const updated = [
        ...prev,
      ];

      for (
        let i =
          updated.length - 1;
        i >= 0;
        i--
      ) {
        if (
          updated[i].role
          === "assistant"
        ) {
          updated[i] = {
            ...updated[i],

            content: text,

            loading,

            sources:
              sources
              ?? updated[i].sources
              ?? [],
          };

          break;
        }
      }

      return updated;
    });
  }


  function finishLastAssistantMessage(
    sources?: Source[]
  ) {
    setMessages((prev) => {
      const updated = [
        ...prev,
      ];

      for (
        let i =
          updated.length - 1;
        i >= 0;
        i--
      ) {
        if (
          updated[i].role
          === "assistant"
        ) {
          updated[i] = {
            ...updated[i],

            loading: false,

            sources:
              sources
              ?? updated[i].sources
              ?? [],
          };

          break;
        }
      }

      return updated;
    });
  }


  function clearMessages() {
    setMessages([
      createWelcomeMessage(),
    ]);

    setLastQuestion("");

    setSelectedHistoryId(
      null
    );
  }


  function loadHistoryConversation(
    question: string,
    answer: string
  ) {
    setMessages([
      {
        id:
          crypto.randomUUID(),

        role:
          "user",

        content:
          question,
      },

      {
        id:
          crypto.randomUUID(),

        role:
          "assistant",

        content:
          answer,

        loading:
          false,

        sources:
          [],
      },
    ]);

    setLastQuestion(
      question
    );
  }


  return (
    <ChatContext.Provider
      value={{
        messages,

        addMessage,

        updateLastAssistantMessage,

        finishLastAssistantMessage,

        clearMessages,

        loadHistoryConversation,

        selectedHistoryId,

        setSelectedHistoryId,

        lastQuestion,

        setLastQuestion,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}


export function useChat() {
  const context =
    useContext(
      ChatContext
    );

  if (!context) {
    throw new Error(
      "useChat must be used inside ChatProvider"
    );
  }

  return context;
}