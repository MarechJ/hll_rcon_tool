import { cmd } from "@/utils/fetchUtils";
import { ChartsReferenceLine } from "@mui/x-charts";
import { LineChart } from "@mui/x-charts/LineChart";
import { useQuery } from "@tanstack/react-query";
import { parseISO } from "date-fns";
import { useState } from "react";

export default function ServerAnalyticsChart() {
  const [days, setDays] = useState(1);
  const [options] = useState({ day: 1, week: 7, month: 30 })

  const { data, isLoading } = useQuery({
    queryKey: ["server-status-analytics", days],
    queryFn: async () =>
      await cmd.GET_SERVER_STATUS_ANALYTICS({ params: { days } }),
    staleTime: 60 * 60 * 1000,
  });

  if (isLoading) {
    return null;
  }

  const dates = data.created_at.map((date) => (date ? parseISO(date) : null));
  const matches = data.matches.filter(match => parseISO(match.start) >= dates[0])

  return (
    <>
      <LineChart
        loading={isLoading}
        xAxis={[{ data: dates, scaleType: "time", label: "Time" }]}
        yAxis={[{ data: [], label: "Players", max: 110 }]}
        series={[
          {
            data: data.total_count,
            label: "Total",
            showMark: false,
            stack: "total",
            id: "Total",
          },
          { data: data.lobby_count, label: "Lobby", showMark: false },
          {
            data: data.axis_count,
            label: "Axis",
            showMark: false,
            color: "#ef4444",
          },
          {
            data: data.allies_count,
            label: "Allies",
            showMark: false,
            color: "#3b82f6",
          },
          { data: data.vip_count, label: "VIP", showMark: false, color: "gold" },
          { data: data.mod_count, label: "Mod", showMark: false },
        ]}
        grid={{ horizontal: true }}
        height={300}
        margin={{ right: 50 }}
        slotProps={{ legend: { hidden: true } }}
      >
        {matches.map((match) => (
          <ChartsReferenceLine
            key={match.id}
            x={parseISO(match.start)}
            lineStyle={{ strokeDasharray: "5 10", opacity: 0.5 }}
          />
        ))}
      </LineChart>
      </>
  );

}
