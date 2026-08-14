import Header from "../../components/Layout/Header";
import Sidebar from "../../components/Layout/Sidebar";
import ChatWindow from "../../components/Chat/ChatWindow";
import ChatInput from "../../components/Chat/ChatInput";


export default function DashboardPage() {
  return (
    <div className="flex h-screen flex-col bg-gray-100">

      <Header />

      <div className="flex min-h-0 flex-1 overflow-hidden">

        <Sidebar />

        <main className="flex min-w-0 flex-1 flex-col">

          <ChatWindow />

          <ChatInput />

        </main>

      </div>

    </div>
  );
}