import { useRef, useEffect } from "react";
import { PanelLeft } from "lucide-react";
import { Message } from "@/pages/Index";
import { ChatMessage } from "./ChatMessage";
import { ChatInputArea } from "./ChatInputArea";
import { WelcomeScreen } from "./WelcomeScreen";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ChatAreaProps {
  messages: Message[];
  isTyping: boolean;
  onSendMessage: (message: string) => void;
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
}

export const ChatArea = ({
  messages,
  isTyping,
  onSendMessage,
  onToggleSidebar,
  sidebarOpen,
}: ChatAreaProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const hasMessages = messages.length > 0;

  return (
    <main className="flex-1 flex flex-col h-full relative">
      {/* Toggle Sidebar Button (when closed) */}
      {!sidebarOpen && (
        <button
          onClick={onToggleSidebar}
          className="absolute top-3 left-3 z-10 w-9 h-9 rounded-lg border border-border bg-background hover:bg-muted flex items-center justify-center transition-colors"
        >
          <PanelLeft className="w-4 h-4 text-foreground" />
        </button>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        {hasMessages ? (
          <ScrollArea className="h-full" ref={scrollRef}>
            <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
              {messages.map((message) => (
                <ChatMessage 
                  key={message.id} 
                  content={message.content} 
                  role={message.role}
                  sql={message.sql}
                  columns={message.columns}
                  rows={message.rows}
                  totalRows={message.totalRows}
                  chartType={message.chartType}
                  chartConfig={message.chartConfig}
                />
              ))}
              {isTyping && <ChatMessage content="" role="assistant" isTyping />}
            </div>
          </ScrollArea>
        ) : (
          <WelcomeScreen onSuggestionClick={onSendMessage} />
        )}
      </div>

      {/* Input Area */}
      <ChatInputArea 
        onSend={onSendMessage} 
        disabled={isTyping}
        showSuggestions={!hasMessages}
      />
    </main>
  );
};
