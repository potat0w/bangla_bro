import { Navbar } from "@/components/Navbar";
import { ChatPanel } from "@/components/chat/ChatPanel";

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar variant="chat" />
      <ChatPanel />
    </div>
  );
}
