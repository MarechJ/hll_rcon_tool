import {Player, PlayerWithStatus} from "@/types/player";
import React from "react";
import {KillDeathChart} from "@/components/game/statistics/team/kill-death-chart";
import {useTranslation} from "react-i18next";
import {RankCompareChart} from "@/components/game/statistics/team/rank-compare-chart";
import {KillCategoryChart} from "@/components/game/statistics/team/kill-category-chart";

export function TeamStats({stats, handlePlayerClick}: {
  stats: Player[] | PlayerWithStatus[]
  handlePlayerClick: (id: string) => void
}) {

  const {t} = useTranslation("game");

  if (stats.length === 0) {
    return null
  }

  return (
    <div className={"grid gap-2"}>
      <h1 className="text-2xl text-center">{t("playerStats.killsByType")}</h1>
      <KillCategoryChart stats={stats} handlePlayerClick={handlePlayerClick}/>
      <h1 className="text-2xl text-center">{t("playerStats.killDiffByTeamRank")}</h1>
      <RankCompareChart stats={stats}/>
      <h1 className="text-2xl text-center">{t("playersTable.kills")}/{t("playersTable.deaths")}</h1>
      <KillDeathChart stats={stats} handlePlayerClick={handlePlayerClick}/>
    </div>
  )
}
