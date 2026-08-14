import { useState } from "react";
import { Check, Copy } from "lucide-react";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";

import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Props {
  language: string;
  value: string;
}

export default function CodeBlock({
  language,
  value,
}: Props) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(value);

    setCopied(true);

    setTimeout(() => {
      setCopied(false);
    }, 2000);
  }

  return (
    <div className="my-4 overflow-hidden rounded-xl border">

      <div className="flex items-center justify-between bg-gray-900 px-4 py-2">

        <span className="text-sm text-gray-300">
          {language}
        </span>

        <button
          onClick={copy}
          className="flex items-center gap-2 text-sm text-white hover:text-green-400"
        >
          {copied ? (
            <>
              <Check size={16} />
              Copied
            </>
          ) : (
            <>
              <Copy size={16} />
              Copy
            </>
          )}
        </button>

      </div>

      <SyntaxHighlighter
        language={language}
        style={oneDark}
        customStyle={{
          margin: 0,
          borderRadius: 0,
        }}
      >
        {value}
      </SyntaxHighlighter>

    </div>
  );
}