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

// Límites de memoria para el frontend
const MAX_CONVERSATIONS = 50; // Máximo 50 conversaciones en memoria
const MAX_MESSAGES_PER_CONVERSATION = 100; // Máximo 100 mensajes por conversación

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
    setConversations((prev) => {
      // Limitar número de conversaciones (mantener las más recientes)
      const updated = [newConversation, ...prev];
      if (updated.length > MAX_CONVERSATIONS) {
        return updated.slice(0, MAX_CONVERSATIONS);
      }
      return updated;
    });
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
      // Preparar historial de conversación (últimas 3-5 interacciones)
      // Solo incluir mensajes que tengan SQL (respuestas del asistente) para contexto
      const conversationHistory = messages
        .slice(-6) // Últimas 6 mensajes (3 interacciones user-assistant)
        .map((msg) => ({
          role: msg.role,
          content: msg.content,
          sql: msg.role === "assistant" ? msg.sql : undefined,
        }))
        .filter((msg) => msg.role === "user" || (msg.role === "assistant" && msg.sql)); // Solo incluir si tiene SQL
      
      // Llamar al backend
      const response = await fetch("/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          question: content,
          conversation_history: conversationHistory.length > 0 ? conversationHistory : undefined
        }),
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

      setMessages((prev) => {
        // Limitar número de mensajes por conversación (mantener los más recientes)
        const updated = [...prev, assistantMessage];
        if (updated.length > MAX_MESSAGES_PER_CONVERSATION) {
          // Mantener solo los últimos MAX_MESSAGES_PER_CONVERSATION mensajes
          return updated.slice(-MAX_MESSAGES_PER_CONVERSATION);
        }
        return updated;
      });
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
