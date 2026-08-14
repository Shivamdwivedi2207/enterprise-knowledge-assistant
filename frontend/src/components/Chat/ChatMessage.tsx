import {
  useState,
} from "react";

import {
  Bot,
  Check,
  Copy,
  User,
} from "lucide-react";

import ReactMarkdown from "react-markdown";

import remarkGfm from "remark-gfm";

import rehypeHighlight from "rehype-highlight";

import type {
  Components,
} from "react-markdown";

import CodeBlock from "./CodeBlock";

import SourceCard from "../Documents/SourceCard";

import type {
  Source,
} from "../../types/chat";


interface Props {
  role:
    | "user"
    | "assistant";

  message: string;

  loading?: boolean;

  sources?: Source[];
}


const markdownComponents:
  Components = {
  code({
    children,
    className,
  }) {
    const match =
      /language-(\w+)/.exec(
        className || ""
      );

    const language =
      match?.[1]
      || "text";

    const value =
      String(
        children
      ).replace(
        /\n$/,
        ""
      );

    if (!match) {
      return (
        <code
          className={
            className
          }
        >
          {children}
        </code>
      );
    }

    return (
      <CodeBlock
        language={
          language
        }
        value={
          value
        }
      />
    );
  },
};


export default function ChatMessage({
  role,
  message,
  loading = false,
  sources = [],
}: Props) {
  const isUser =
    role === "user";

  const [
    copied,
    setCopied,
  ] = useState(false);


  async function copyMessage() {
    if (!message) {
      return;
    }

    await navigator
      .clipboard
      .writeText(
        message
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


  return (
    <div
      className={`mb-8 flex ${
        isUser
          ? "justify-end"
          : "justify-start"
      }`}
    >
      <div
        className={`flex max-w-5xl gap-3 ${
          isUser
            ? "flex-row-reverse"
            : "flex-row"
        }`}
      >

        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
            isUser
              ? "bg-blue-600 text-white"
              : "bg-green-600 text-white"
          }`}
        >
          {isUser ? (
            <User
              size={18}
            />
          ) : (
            <Bot
              size={18}
            />
          )}
        </div>

        <div
          className={`relative rounded-2xl px-5 py-4 shadow-sm ${
            isUser
              ? (
                "bg-blue-600 "
                + "text-white"
              )
              : (
                "border "
                + "border-gray-200 "
                + "bg-white"
              )
          }`}
        >

          {!isUser
            && message
            && !loading
            && (
              <button
                onClick={() => {
                  void copyMessage();
                }}
                className="
                  absolute
                  right-3
                  top-3
                  rounded-md
                  p-1
                  transition
                  hover:bg-gray-100
                "
                title="Copy response"
              >
                {copied ? (
                  <Check
                    size={18}
                    className="text-green-600"
                  />
                ) : (
                  <Copy
                    size={18}
                    className="text-gray-600"
                  />
                )}
              </button>
            )}

          {isUser ? (
            <div className="whitespace-pre-wrap break-words">
              {message}
            </div>
          ) : (
            <>
              <div className="prose prose-sm max-w-none pr-7">

                {message ? (
                  <ReactMarkdown
                    remarkPlugins={[
                      remarkGfm,
                    ]}
                    rehypePlugins={[
                      rehypeHighlight,
                    ]}
                    components={
                      markdownComponents
                    }
                  >
                    {message}
                  </ReactMarkdown>
                ) : (
                  loading && (
                    <span className="text-sm text-gray-500">
                      Thinking...
                    </span>
                  )
                )}

                {loading && (
                  <span className="typing-cursor ml-1">
                    ▌
                  </span>
                )}

              </div>

              {sources.length > 0
                && !loading
                && (
                  <div className="mt-6 border-t border-gray-200 pt-4">

                    <div className="mb-3 text-sm font-semibold text-gray-700">
                      📄 Sources
                    </div>

                    <div className="space-y-3">
                      {sources.map(
                        (
                          source,
                          index
                        ) => (
                          <SourceCard
                            key={
                              `${source.document_id}-${source.chunk_index}-${index}`
                            }
                            source={
                              source
                            }
                          />
                        )
                      )}
                    </div>

                  </div>
                )}

            </>
          )}

        </div>

      </div>
    </div>
  );
}