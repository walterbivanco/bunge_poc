import { Database } from "lucide-react";

interface WelcomeScreenProps {
  onSuggestionClick: (message: string) => void;
}

const SUGGESTIONS = [
  "How many contracts are there by status?",
  "Show me the last 10 contracts",
  "SOYBEAN contracts in 2025",
  "What is the average price per product?",
];

export const WelcomeScreen = ({ onSuggestionClick }: WelcomeScreenProps) => {
  return (
    <div className="h-full flex flex-col items-center justify-center px-4">
      <div className="text-center max-w-xl animate-fade-in">
        <div className="w-16 h-16 rounded-2xl bg-secondary mx-auto mb-6 flex items-center justify-center">
          <Database className="w-8 h-8 text-secondary-foreground" />
        </div>
        <h1 className="text-2xl font-bold text-foreground mb-2">
          NL → SQL Chatbot
        </h1>
        <p className="text-lg text-muted-foreground mb-6">
          Ask questions in natural language about your data
        </p>
        
        {/* Suggestions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-6">
          {SUGGESTIONS.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => onSuggestionClick(suggestion)}
              className="text-left px-4 py-3 rounded-xl border border-border bg-card hover:bg-muted transition-colors text-sm text-foreground"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
