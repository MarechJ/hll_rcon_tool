import {Player, PlayerWithStatus} from "@/types/player";
import React from "react";
import {
  CartesianGrid,
  Cell, ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  Tooltip, TooltipProps,
  XAxis,
  YAxis
} from "recharts";
import {getColorForTeam} from "@/components/game/statistics/utils";
import {useTranslation} from "react-i18next";
import colors from "tailwindcss/colors";

export function KillDeathChart({stats, handlePlayerClick}: {
  stats: Player[] | PlayerWithStatus[]
  handlePlayerClick: (id: string) => void
}) {

  const {t} = useTranslation("game");

  const maxKills = Math.max.apply(null, stats.map(player => player.kills));
  const maxDeaths = Math.max.apply(null, stats.map(player => player.deaths));

  return (
    <div className={"h-[90vh] w-full"}>
      <ResponsiveContainer height={"100%"} width={"100%"}>
        <ComposedChart
          data={stats}
          margin={{
            top: 20,
            right: 20,
            bottom: 20,
            left: 20,
          }}
        >
          <XAxis type="number" dataKey="deaths" name={t("playersTable.deaths")} label={t("playersTable.deaths")} domain={[0, maxDeaths]} tickCount={1}/>
          <YAxis type="number" dataKey="kills" name={t("playersTable.kills")} label={t("playersTable.kills")} domain={[0, maxKills]} tickCount={1}/>
          <Line dataKey="kills" tooltipType="none" stroke={colors.purple[600]} dot={false} activeDot={false} legendType="none" data={[{kills: 0, deaths: 0}, {kills: maxKills, deaths: maxDeaths}]} />
          <Scatter data={stats}>
            {stats.map((player, index) => (
              <Cell key={`cell-${index}`} fill={getColorForTeam(player.team)} onClick={() => handlePlayerClick(player.player_id)} onMouse/>
            ))}
          </Scatter>

        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}


