import {
  useState,
} from "react";

import {
  FileText,
  History,
} from "lucide-react";

import UploadBox from "../Documents/UploadBox";
import DocumentList from "../Documents/DocumentList";
import ChatHistoryPanel from "../Chat/ChatHistoryPanel";


type SidebarTab =
  | "documents"
  | "history";


export default function Sidebar() {
  const [
    activeTab,
    setActiveTab,
  ] = useState<SidebarTab>(
    "documents"
  );


  return (
    <aside
      className="
        flex
        w-80
        shrink-0
        flex-col
        border-r
        border-gray-200
        bg-white
      "
    >
      {/* =====================================================
          Tabs
      ===================================================== */}

      <div className="border-b border-gray-200 p-3">

        <div className="grid grid-cols-2 gap-2">

          {/* Documents */}

          <button
            type="button"
            onClick={() =>
              setActiveTab(
                "documents"
              )
            }
            className={`
              flex
              items-center
              justify-center
              gap-2
              rounded-lg
              px-3
              py-2
              text-sm
              font-medium
              transition
              ${
                activeTab === "documents"
                  ? (
                    "bg-blue-600 "
                    + "text-white"
                  )
                  : (
                    "bg-gray-100 "
                    + "text-gray-600 "
                    + "hover:bg-gray-200"
                  )
              }
            `}
          >
            <FileText
              size={17}
            />

            Documents
          </button>


          {/* Chat History */}

          <button
            type="button"
            onClick={() =>
              setActiveTab(
                "history"
              )
            }
            className={`
              flex
              items-center
              justify-center
              gap-2
              rounded-lg
              px-3
              py-2
              text-sm
              font-medium
              transition
              ${
                activeTab === "history"
                  ? (
                    "bg-blue-600 "
                    + "text-white"
                  )
                  : (
                    "bg-gray-100 "
                    + "text-gray-600 "
                    + "hover:bg-gray-200"
                  )
              }
            `}
          >
            <History
              size={17}
            />

            History
          </button>

        </div>

      </div>


      {/* =====================================================
          Documents Tab
      ===================================================== */}

      {activeTab === "documents" && (
        <div className="flex min-h-0 flex-1 flex-col">

          {/* Upload */}

          <div className="border-b border-gray-100 p-5">
            <UploadBox />
          </div>


          {/* Uploaded Documents */}

          <div className="min-h-0 flex-1 overflow-y-auto">
            <DocumentList />
          </div>

        </div>
      )}


      {/* =====================================================
          Chat History Tab
      ===================================================== */}

      {activeTab === "history" && (
        <div className="min-h-0 flex-1 overflow-y-auto">

          <ChatHistoryPanel />

        </div>
      )}

    </aside>
  );
}