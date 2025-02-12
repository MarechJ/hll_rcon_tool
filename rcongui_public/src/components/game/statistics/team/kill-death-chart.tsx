import {Player, PlayerWithStatus} from '@/types/player'
import React from 'react'
import {Cell, ComposedChart, Label, ReferenceLine, ResponsiveContainer, Scatter, XAxis, YAxis} from 'recharts'
import {generateTicks, getColorForTeam, getTeamFromAssociation} from '@/components/game/statistics/utils'
import {useTranslation} from 'react-i18next'
import colors from 'tailwindcss/colors'

export function KillDeathChart({stats, handlePlayerClick}: {
  stats: Player[] | PlayerWithStatus[]
  handlePlayerClick: (id: string) => void
}) {

  const {t} = useTranslation("game");

  const maxKills = Math.max.apply(null, stats.map(player => player.kills));
  const maxDeaths = Math.max.apply(null, stats.map(player => player.deaths));

  const referenceLinesKd = [0.5, 1, 2];

  return (
    <div className={"h-[80vh] w-full"}>
      <ResponsiveContainer height={"100%"} width={"100%"}>
        <ComposedChart
          data={stats}
          margin={{
            top: 20,
            right: 20,
            bottom: 20,
          }}
        >
          <XAxis type="number" dataKey="deaths" name={t("playersTable.deaths")} label={t("playersTable.deaths")} domain={[0, maxDeaths]} ticks={generateTicks(maxDeaths, 50)}/>
          <YAxis type="number" dataKey="kills" name={t("playersTable.kills")} label={t("playersTable.kills")} domain={[0, maxKills]} ticks={generateTicks(maxKills, 50)}/>
          {referenceLinesKd.map(kd =>
            <ReferenceLine key={kd} stroke={colors.purple[600]} strokeDasharray={kd === 1 ? undefined : "3 3"} segment={[{ x: 0, y: 0 }, { x: Math.min(maxKills, maxDeaths), y: Math.min(maxKills,maxDeaths) * kd }]} ifOverflow="visible">
              <Label>
                {kd + " K/D"}
              </Label>
            </ReferenceLine>
          )}
          <Scatter data={stats}>
            {stats.map((player, index) => (
              <Cell key={`cell-${index}`} fill={getColorForTeam(getTeamFromAssociation(player.team))} onClick={() => handlePlayerClick(player.player_id)} className="cursor-pointer"/>
            ))}
          </Scatter>

        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}


