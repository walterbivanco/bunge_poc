import { useState, KeyboardEvent } from "react";
import { ArrowUp, Paperclip } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputAreaProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  showSuggestions?: boolean;
}

const SUGGESTIONS = [
  "What are Bunge's main products?",
  "Information about sustainable agriculture",
  "How can I contact support?",
  "Tell me about Bunge's global presence",
];

export const ChatInputArea = ({ onSend, disabled, showSuggestions }: ChatInputAreaProps) => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (!disabled) {
      onSend(suggestion);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4 pb-6 pt-2">
      {/* Suggestions */}
      {showSuggestions && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4 animate-fade-in">
          {SUGGESTIONS.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              disabled={disabled}
              className="text-left px-4 py-3 rounded-xl border border-border bg-card hover:bg-muted transition-colors text-sm text-foreground disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      {/* Input Container */}
      <div className="relative rounded-2xl border border-border bg-card shadow-sm overflow-hidden">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send a message..."
          disabled={disabled}
          rows={1}
          className={cn(
            "w-full resize-none bg-transparent px-4 pt-4 pb-14 text-sm",
            "placeholder:text-muted-foreground",
            "focus:outline-none",
            "disabled:cursor-not-allowed disabled:opacity-50",
            "min-h-[56px] max-h-[200px]"
          )}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = "auto";
            target.style.height = Math.min(target.scrollHeight, 200) + "px";
          }}
        />

        {/* Bottom Bar */}
        <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between px-3 py-2 bg-card">
          <div className="flex items-center gap-2">
            <button
              className="w-8 h-8 rounded-lg hover:bg-muted flex items-center justify-center transition-colors"
              title="Attach file"
            >
              <Paperclip className="w-4 h-4 text-muted-foreground" />
            </button>
            <span className="text-xs text-muted-foreground">Virtual Assistant</span>
          </div>
          <button
            onClick={handleSend}
            disabled={disabled || !message.trim()}
            className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-200",
              message.trim() && !disabled
                ? "bg-primary text-primary-foreground hover:opacity-90"
                : "bg-muted text-muted-foreground cursor-not-allowed"
            )}
          >
            <ArrowUp className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
