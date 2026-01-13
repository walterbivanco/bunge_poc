import { Plus, MessageSquare, PanelLeftClose } from "lucide-react";
import { cn } from "@/lib/utils";
import { Conversation } from "@/pages/Index";
import { ScrollArea } from "@/components/ui/scroll-area";
import logoBunge from "@/assets/logo-bunge.svg";

interface ChatSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
}

export const ChatSidebar = ({
  isOpen,
  onToggle,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
}: ChatSidebarProps) => {
  return (
    <aside
      className={cn(
        "h-full bg-sidebar border-r border-sidebar-border flex flex-col transition-all duration-300 ease-out",
        isOpen ? "w-64" : "w-0 overflow-hidden"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-center p-3 border-b border-sidebar-border relative">
        <img src={logoBunge} alt="Bunge" className="h-6" />
        <button
          onClick={onToggle}
          className="w-8 h-8 rounded-lg hover:bg-sidebar-accent flex items-center justify-center transition-colors absolute right-3"
        >
          <PanelLeftClose className="w-4 h-4 text-sidebar-foreground" />
        </button>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg border border-border hover:bg-sidebar-accent transition-colors text-sm font-medium text-sidebar-foreground"
        >
          <Plus className="w-4 h-4" />
          New conversation
        </button>
      </div>

      {/* Conversations List */}
      <ScrollArea className="flex-1 px-3">
        <div className="space-y-1 pb-4">
          {conversations.length === 0 ? (
            <p className="text-xs text-muted-foreground text-center py-8 px-2">
              Your conversations will appear here
            </p>
          ) : (
            conversations.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => onSelectConversation(conversation.id)}
                className={cn(
                  "w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-left transition-colors text-sm",
                  activeConversationId === conversation.id
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent/50"
                )}
              >
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{conversation.title}</span>
              </button>
            ))
          )}
        </div>
      </ScrollArea>
    </aside>
  );
};
