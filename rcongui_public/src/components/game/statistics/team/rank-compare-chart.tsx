import {Player, PlayerWithStatus, TeamEnum} from '@/types/player'
import React from 'react'
import {Bar, BarChart, CartesianGrid, Cell, Label, ReferenceLine, ResponsiveContainer, XAxis, YAxis} from 'recharts'
import {generateTicks, getColorForTeam} from '@/components/game/statistics/utils'
import {useTranslation} from 'react-i18next'
import colors from "tailwindcss/colors";

export function RankCompareChart({stats}: {
  stats: Player[] | PlayerWithStatus[]
}) {

  const {t} = useTranslation("game");

  const axisPlayers = stats.filter(player => player.team.side === TeamEnum.AXIS).sort((a, b) => b.kills - a.kills);
  const alliesPlayers = stats.filter(player => player.team.side === TeamEnum.ALLIES).sort((a, b) => b.kills - a.kills);

  const data = axisPlayers.map((axisPlayer, index) => ({rank: index + 1, kills: alliesPlayers[index] ? axisPlayer.kills - alliesPlayers[index].kills : null}));

  const maxDiff = data.reduce((prev, current) => current.kills && Math.abs(current.kills) > prev ? Math.abs(current.kills) : prev, 0);

  const referenceLines = [-10, -5, 0, 5, 10];

  return (
    <div className={"h-[40vh] w-full"}>
      <ResponsiveContainer height={"100%"} width={"100%"}>
        <BarChart
          width={500}
          height={300}
          data={data}
          margin={{
            top: 20,
            right: 20,
            bottom: 20,
          }}
        >
          {referenceLines.map(reference =>
            <ReferenceLine stroke={colors.purple[600]} strokeDasharray={"3 3"} segment={[{ x: 0, y: reference }, { x: data.length, y: reference }]} ifOverflow="hidden">
            </ReferenceLine>
          )}
          <XAxis dataKey="rank" label={t("playerStats.teamRank")} ticks={generateTicks(data.length, 10)}/>
          <YAxis label={t("playerStats.killDiff")} ticks={generateTicks(maxDiff, 10, true)}/>
          <Bar dataKey="kills" fill="#8884d8">
            {data.map((entry, index) => (
              <Cell fill={entry.kills && entry.kills > 0 ? getColorForTeam(TeamEnum.AXIS) : getColorForTeam(TeamEnum.ALLIES)} key={`cell-${index}`} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}


