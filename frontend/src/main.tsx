import React from "react";
import ReactDOM from "react-dom/client";
import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";

import App from "./App";

import { ChatProvider } from "./context/ChatContext";
import { SourcePreviewProvider } from "./context/SourcePreviewContext";

import "./index.css";

const queryClient = new QueryClient();

ReactDOM.createRoot(
  document.getElementById("root")!
).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>

      <ChatProvider>

        <SourcePreviewProvider>

          <Toaster position="top-right" />

          <App />

        </SourcePreviewProvider>

      </ChatProvider>

    </QueryClientProvider>
  </React.StrictMode>
);