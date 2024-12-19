import {Player, PlayerWithStatus} from "@/types/player";
import React from "react";
import {Cell, ComposedChart, Label, ReferenceLine, ResponsiveContainer, Scatter, XAxis, YAxis} from "recharts";
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

  const referenceLinesKpm = [0.5, 1, 2];

  const generateTicks = (n: number) => {
    const interval = 50;
    const ticks = [];
    for (let i = 1; i < n / interval; i++) {
      ticks.push(i * interval);
    }
    ticks.push(n);
    return ticks;
  }

  return (
    <div className={"h-[80vh] w-full"}>
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
          <XAxis type="number" dataKey="deaths" name={t("playersTable.deaths")} label={t("playersTable.deaths")} domain={[0, maxDeaths]} ticks={generateTicks(maxDeaths)}/>
          <YAxis type="number" dataKey="kills" name={t("playersTable.kills")} label={t("playersTable.kills")} domain={[0, maxKills]} ticks={generateTicks(maxKills)}/>
          {referenceLinesKpm.map(kpm =>
            <ReferenceLine stroke={colors.purple[600]} strokeDasharray={kpm === 1 ? undefined : "3 3"} segment={[{ x: 0, y: 0 }, { x: Math.min(maxKills, maxDeaths), y: Math.min(maxKills,maxDeaths) * kpm }]} ifOverflow="visible">
              <Label>
                {kpm + " kpm"}
              </Label>
            </ReferenceLine>
          )}
          <Scatter data={stats}>
            {stats.map((player, index) => (
              <Cell key={`cell-${index}`} fill={getColorForTeam(player.team)} onClick={() => handlePlayerClick(player.player_id)} className="cursor-pointer"/>
            ))}
          </Scatter>

        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}


