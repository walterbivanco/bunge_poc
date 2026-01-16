import { cn } from "@/lib/utils";
import { Bot, User } from "lucide-react";
import { DataChart } from "./DataChart";
import { ChartData } from "@/lib/chartUtils";

interface ChatMessageProps {
  content: string;
  role: "user" | "assistant";
  isTyping?: boolean;
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

export const ChatMessage = ({ 
  content, 
  role, 
  isTyping, 
  sql, 
  columns, 
  rows, 
  totalRows,
  chartType,
  chartConfig
}: ChatMessageProps) => {
  const isUser = role === "user";
  
  // Build chart data from LLM recommendation
  let chartData: ChartData | null = null;
  if (chartType && chartConfig && columns && rows && rows.length > 0) {
    let xKey = chartConfig.xKey;
    let yKey = chartConfig.yKey;
    
    // Fallback if keys not provided
    if (!xKey) xKey = columns[0];
    if (!yKey) yKey = columns.length > 1 ? columns[1] : columns[0];
    
    // Find column indices
    const xColIdx = columns.indexOf(xKey);
    let yColIdx = columns.indexOf(yKey);
    
    // For pie charts, if yKey is "value", we count occurrences
    if (chartType === "pie" && yKey === "value") {
      const categoryCounts = new Map<string, number>();
      rows.forEach((row) => {
        const category = String(row[xColIdx] || "Unknown");
        categoryCounts.set(category, (categoryCounts.get(category) || 0) + 1);
      });
      
      chartData = {
        type: "pie",
        data: Array.from(categoryCounts.entries()).map(([name, value]) => ({
          name: name.slice(0, 30),
          value,
        })),
        xKey: "name",
        yKey: "value",
        label: "Count",
      };
    } else if (xColIdx >= 0 && (yColIdx >= 0 || chartType === "pie")) {
      // For other chart types
      chartData = {
        type: chartType as "bar" | "line" | "pie" | "area",
        data: rows.map((row) => {
          const dataPoint: any = {};
          
          if (chartType === "pie") {
            // Pie chart with explicit value column
            dataPoint.name = String(row[xColIdx] || "Unknown").slice(0, 30);
            const yValue = yColIdx >= 0 ? row[yColIdx] : 1;
            dataPoint.value = typeof yValue === "number" ? yValue : (typeof yValue === "string" ? parseFloat(yValue) || 1 : 1);
          } else {
            // Bar, line, or area chart
            dataPoint[xKey] = row[xColIdx] !== null && row[xColIdx] !== undefined ? String(row[xColIdx]) : "";
            const yValue = row[yColIdx];
            dataPoint[yKey] = typeof yValue === "number" ? yValue : (typeof yValue === "string" ? parseFloat(yValue) || 0 : 0);
          }
          
          return dataPoint;
        }),
        xKey: chartType === "pie" ? "name" : xKey,
        yKey: chartType === "pie" ? "value" : yKey,
        label: chartType === "pie" ? "Count" : yKey,
      };
    }
  }

  return (
    <div
      className={cn(
        "flex gap-4 animate-fade-in",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
          isUser ? "bg-primary" : "bg-secondary"
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-primary-foreground" />
        ) : (
          <Bot className="w-4 h-4 text-secondary-foreground" />
        )}
      </div>

      {/* Message Content */}
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-3",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground"
        )}
      >
        {isTyping ? (
          <div className="flex gap-1.5 py-1 px-1">
            <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
            <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
            <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
          </div>
        ) : (
          <div className="space-y-3">
            {content && (
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
            )}
            
            {/* SQL Query */}
            {sql && (
              <div className="mt-3">
                <details className="group" open>
                  <summary className="text-xs font-mono text-muted-foreground cursor-pointer hover:text-foreground select-none">
                    View generated SQL
                  </summary>
                  <div className="mt-2 bg-background rounded-lg border border-border">
                    <div className="p-3 max-h-96 overflow-auto">
                      <code className="text-xs font-mono whitespace-pre-wrap break-words block leading-relaxed">
                        {sql}
                      </code>
                    </div>
                  </div>
                </details>
              </div>
            )}

            {/* Chart Visualization */}
            {chartData && (
              <DataChart chartData={chartData} />
            )}

            {/* Data Table */}
            {columns && rows && rows.length > 0 && (
              <div className="mt-3 overflow-x-auto">
                <div className="rounded-lg border border-border overflow-hidden">
                  <table className="w-full text-xs">
                    <thead className="bg-muted/50">
                      <tr>
                        {columns.map((col, idx) => (
                          <th
                            key={idx}
                            className="px-3 py-2 text-left font-semibold text-foreground border-b border-border"
                          >
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.slice(0, 100).map((row, rowIdx) => (
                        <tr
                          key={rowIdx}
                          className="border-b border-border last:border-b-0 hover:bg-muted/30"
                        >
                          {row.map((cell, cellIdx) => (
                            <td
                              key={cellIdx}
                              className="px-3 py-2 text-foreground"
                            >
                              {cell !== null && cell !== undefined
                                ? String(cell)
                                : "—"}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {totalRows && totalRows > 100 && (
                    <div className="px-3 py-2 text-xs text-muted-foreground bg-muted/30 border-t border-border">
                      Showing 100 of {totalRows} results
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
