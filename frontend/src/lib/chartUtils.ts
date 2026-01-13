/**
 * Chart types and data structures
 * Chart recommendations are now provided by the LLM (Gemini) in the backend
 */

export type ChartType = "bar" | "line" | "pie" | "area" | null;

export interface ChartData {
  type: ChartType;
  data: any[];
  xKey: string;
  yKey: string;
  label?: string;
}
