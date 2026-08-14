import {
  useEffect,
  useRef,
} from "react";

import ChatMessage from "./ChatMessage";

import {
  useChat,
} from "../../context/ChatContext";


export default function ChatWindow() {
  const {
    messages,
  } = useChat();

  const bottomRef =
    useRef<HTMLDivElement>(
      null
    );


  useEffect(() => {
    bottomRef
      .current
      ?.scrollIntoView({
        behavior:
          "smooth",
        block:
          "end",
      });
  }, [messages]);


  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 p-6">

      <div className="mx-auto w-full max-w-6xl">

        {messages.map(
          (message) => (
            <ChatMessage
              key={
                message.id
              }
              role={
                message.role
              }
              message={
                message.content
              }
              loading={
                message.loading
              }
              sources={
                message.sources
              }
            />
          )
        )}

        <div
          ref={
            bottomRef
          }
        />

      </div>

    </div>
  );
}