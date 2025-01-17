import {Player, PlayerWithStatus, TeamEnum} from '@/types/player'
import React from 'react'
import {Bar, BarChart, Cell, ReferenceLine, ResponsiveContainer, Tooltip, TooltipProps, XAxis, YAxis} from 'recharts'
import {generateTicks, getColorForTeam} from '@/components/game/statistics/utils'
import {useTranslation} from 'react-i18next'
import colors from "tailwindcss/colors";
import {NameType, ValueType} from "recharts/types/component/DefaultTooltipContent";
import {TeamIndicator} from "@/components/game/statistics/team-indicator";

export function RankCompareChart({stats}: {
  stats: Player[] | PlayerWithStatus[]
}) {

  const {t} = useTranslation("game");

  const axisPlayers = stats.filter(player => player.team.side === TeamEnum.AXIS).sort((a, b) => b.kills - a.kills);
  const alliesPlayers = stats.filter(player => player.team.side === TeamEnum.ALLIES).sort((a, b) => b.kills - a.kills);

  const data = axisPlayers.map((axisPlayer, index) => ({rank: index + 1, kills: alliesPlayers[index] ? axisPlayer.kills - alliesPlayers[index].kills : null, axisPlayer: axisPlayer, alliesPlayer: alliesPlayers[index]}));

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
          <Tooltip content={<CustomTooltip/>}/>
          {referenceLines.map(reference =>
            <ReferenceLine key={reference} stroke={colors.purple[600]} strokeDasharray={"3 3"} y={reference} ifOverflow="hidden">
            </ReferenceLine>
          )}
          <XAxis dataKey="rank" label={t("playerStats.teamRank")} ticks={generateTicks(data.length, 10)}/>
          <YAxis label={t("playerStats.killDiff")} ticks={generateTicks(maxDiff, 10, true)}/>
          <Bar dataKey="kills" fill="#8884d8" isAnimationActive={false}>
            {data.map((entry, index) => (
              <Cell fill={entry.kills && entry.kills > 0 ? getColorForTeam(TeamEnum.AXIS) : getColorForTeam(TeamEnum.ALLIES)} key={`cell-${index}`} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

const CustomTooltip = ({
                         active,
                         payload,
                       }: TooltipProps<ValueType, NameType>) =>
{
  const {t} = useTranslation("game");
  if (active && payload && payload.length) {
    return (
      <div className="bg-background border p-2 flex flex-col">
        <span>
          {t('playerStats.rank')}: #{payload[0].payload.rank} ({payload[0].payload.kills})
        </span>
        <span>
          <TeamIndicator
            team={TeamEnum.AXIS}/> {payload[0].payload.axisPlayer.kills} {payload[0].payload.axisPlayer.player}
        </span>
        <span>
          <TeamIndicator
            team={TeamEnum.ALLIES}/> {payload[0].payload.alliesPlayer.kills} {payload[0].payload.alliesPlayer.player}
        </span>
      </div>
    );
  }

  return null;
};

