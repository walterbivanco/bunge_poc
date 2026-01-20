import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, CartesianGrid, Legend } from "recharts";
import { ChartData } from "@/lib/chartUtils";
import { cn, formatColumnName } from "@/lib/utils";

interface DataChartProps {
  chartData: ChartData;
  className?: string;
}

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
];

export const DataChart = ({ chartData, className }: DataChartProps) => {
  if (!chartData || !chartData.data || chartData.data.length === 0) {
    return null;
  }

  const chartConfig: Record<string, { label: string; color?: string }> = {
    [chartData.yKey]: {
      label: chartData.label ? formatColumnName(chartData.label) : formatColumnName(chartData.yKey),
      color: COLORS[0],
    },
    // Agregar también el xKey para formatear nombres dinámicos
    [chartData.xKey]: {
      label: formatColumnName(chartData.xKey),
      color: COLORS[0],
    },
  };

  const renderChart = () => {
    switch (chartData.type) {
      case "bar":
        return (
          <BarChart data={chartData.data} margin={{ top: 5, right: 10, left: 0, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
            <XAxis
              dataKey={chartData.xKey}
              tick={{ fontSize: 11 }}
              angle={chartData.data.length > 5 ? -45 : 0}
              textAnchor={chartData.data.length > 5 ? "end" : "middle"}
              height={chartData.data.length > 5 ? 80 : 40}
              label={{ value: formatColumnName(chartData.xKey), position: "insideBottom", offset: -5, style: { textAnchor: "middle", fontSize: 12 } }}
            />
            <YAxis 
              tick={{ fontSize: 11 }}
              label={{ value: formatColumnName(chartData.yKey), angle: -90, position: "insideLeft", style: { textAnchor: "middle", fontSize: 12 } }}
            />
            <ChartTooltip 
              content={
                <ChartTooltipContent 
                  formatter={(value, name) => [
                    typeof value === 'number' ? value.toLocaleString() : value,
                    formatColumnName(String(name || chartData.yKey))
                  ]}
                />
              } 
            />
            <Bar dataKey={chartData.yKey} fill={COLORS[0]} radius={[4, 4, 0, 0]} />
          </BarChart>
        );

      case "line":
        return (
          <LineChart data={chartData.data} margin={{ top: 5, right: 10, left: 0, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
            <XAxis
              dataKey={chartData.xKey}
              tick={{ fontSize: 11 }}
              angle={chartData.data.length > 5 ? -45 : 0}
              textAnchor={chartData.data.length > 5 ? "end" : "middle"}
              height={chartData.data.length > 5 ? 80 : 40}
              label={{ value: formatColumnName(chartData.xKey), position: "insideBottom", offset: -5, style: { textAnchor: "middle", fontSize: 12 } }}
            />
            <YAxis 
              tick={{ fontSize: 11 }}
              label={{ value: formatColumnName(chartData.yKey), angle: -90, position: "insideLeft", style: { textAnchor: "middle", fontSize: 12 } }}
            />
            <ChartTooltip 
              content={
                <ChartTooltipContent 
                  formatter={(value, name) => [
                    typeof value === 'number' ? value.toLocaleString() : value,
                    formatColumnName(String(name || chartData.yKey))
                  ]}
                />
              } 
            />
            <Line
              type="monotone"
              dataKey={chartData.yKey}
              stroke={COLORS[0]}
              strokeWidth={2}
              dot={{ r: chartData.data.length > 20 ? 0 : 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        );

      case "area":
        return (
          <AreaChart data={chartData.data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey={chartData.xKey}
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
              label={{ value: formatColumnName(chartData.xKey), position: "insideBottom", offset: -5, style: { textAnchor: "middle", fontSize: 12 } }}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              label={{ value: formatColumnName(chartData.yKey), angle: -90, position: "insideLeft", style: { textAnchor: "middle", fontSize: 12 } }}
            />
            <ChartTooltip 
              content={
                <ChartTooltipContent 
                  formatter={(value, name) => [
                    typeof value === 'number' ? value.toLocaleString() : value,
                    formatColumnName(String(name || chartData.yKey))
                  ]}
                />
              } 
            />
            <Area
              type="monotone"
              dataKey={chartData.yKey}
              stroke={COLORS[0]}
              fill={COLORS[0]}
              fillOpacity={0.6}
            />
          </AreaChart>
        );

      case "pie":
        return (
          <PieChart>
            <Pie
              data={chartData.data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey={chartData.yKey}
            >
              {chartData.data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <ChartTooltip 
              content={
                <ChartTooltipContent 
                  formatter={(value, name) => [
                    typeof value === 'number' ? value.toLocaleString() : value,
                    formatColumnName(String(name || chartData.yKey))
                  ]}
                />
              } 
            />
          </PieChart>
        );

      default:
        return null;
    }
  };

  return (
    <div className={cn("w-full mt-3", className)}>
      <ChartContainer config={chartConfig} className="h-[300px] w-full">
        {renderChart()}
      </ChartContainer>
    </div>
  );
};
