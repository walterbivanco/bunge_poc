import { useState } from "react";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatArea } from "@/components/chat/ChatArea";

export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
}

export interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  sql?: string;
  columns?: string[];
  rows?: any[][];
  totalRows?: number;
  chartType?: string | null;
  chartConfig?: {
    xKey?: string;
    yKey?: string;
  } | null;
}

const Index = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: "New conversation",
      createdAt: new Date(),
    };
    setConversations((prev) => [newConversation, ...prev]);
    setActiveConversationId(newConversation.id);
    setMessages([]);
  };

  const handleSendMessage = async (content: string) => {
    // Create conversation if none exists
    if (!activeConversationId) {
      const newConversation: Conversation = {
        id: Date.now().toString(),
        title: content.slice(0, 30) + (content.length > 30 ? "..." : ""),
        createdAt: new Date(),
      };
      setConversations((prev) => [newConversation, ...prev]);
      setActiveConversationId(newConversation.id);
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: "user",
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      // Llamar al backend
      const response = await fetch("/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: content }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error processing query");
      }

      const data = await response.json();
      
      // Build response message
      let responseContent = "";
      if (data.total_rows > 0) {
        responseContent = `Found ${data.total_rows} result${data.total_rows !== 1 ? "s" : ""}:\n\n`;
      } else {
        responseContent = "Query executed successfully but no results found.\n\n";
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: responseContent,
        role: "assistant",
        sql: data.sql,
        columns: data.columns,
        rows: data.rows,
        totalRows: data.total_rows,
        chartType: data.chart_type || null,
        chartConfig: data.chart_config || null,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `❌ Error: ${error instanceof Error ? error.message : "Unknown error"}`,
        role: "assistant",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="h-screen flex bg-background overflow-hidden">
      <ChatSidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={(id) => setActiveConversationId(id)}
        onNewConversation={createNewConversation}
      />
      <ChatArea
        messages={messages}
        isTyping={isTyping}
        onSendMessage={handleSendMessage}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        sidebarOpen={sidebarOpen}
      />
    </div>
  );
};

export default Index;
