import { cmd } from "@/utils/fetchUtils";
import { LineChart } from "@mui/x-charts/LineChart";
import { useQuery } from "@tanstack/react-query";
import { parseISO } from "date-fns";
import { useState } from "react";

export default function ServerUsageAnalyticsChart() {
  const [days, setDays] = useState(1);
  const [options] = useState({ day: 1, week: 7, month: 30 })

  const { data, isLoading } = useQuery({
    queryKey: ["server-usage-analytics", days],
    queryFn: async () =>
      await cmd.GET_SYSTEM_USAGE_ANALYTICS({ params: { days } }),
    staleTime: 60 * 60 * 1000,
  });

  if (isLoading) {
    return null;
  }

  console.log(data)

  const dates = data.created_at.map((date) => (date ? parseISO(date) : null));

  return (
    <LineChart
      loading={isLoading}
      xAxis={[{ data: dates, scaleType: "time", label: "Time" }]}
      yAxis={[{ data: [], label: "Usage %", max: 110 }]}
      series={[
        ...Object.entries(data.player_counts).map(([server, counts]) => ({
          data: counts.map(value => value / Object.keys(data.player_counts).length),
          valueFormatter: (value) => value * Object.keys(data.player_counts).length,
          label: `#${server}`,
          showMark: false,
          stack: "total",
          area: true,
        })),
        {
          data: data.cpu_percent,
          label: "CPU %",
          showMark: false,
          color: "#ef4444",
        },
        {
          data: data.ram_percent,
          label: "RAM &",
          showMark: false,
          color: "#ab4444",
        },
      ]}
      grid={{ horizontal: true }}
      height={300}
      margin={{ right: 50 }}
      slotProps={{ legend: { hidden: true } }}
    >
    </LineChart>
  );
}
