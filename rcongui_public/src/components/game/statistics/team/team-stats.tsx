import {Player, PlayerWithStatus} from "@/types/player";
import React from "react";
import {KillDeathChart} from "@/components/game/statistics/team/kill-death-chart";
import {useTranslation} from "react-i18next";

export function TeamStats({stats, handlePlayerClick}: {
  stats: Player[] | PlayerWithStatus[]
  handlePlayerClick: (id: string) => void
}) {

  const {t} = useTranslation("game");

  if (stats.length === 0) {
    return null
  }

  return (
    <>
      <h1 className="text-2xl text-center">{t("playersTable.kills")}/{t("playersTable.deaths")}</h1>
      <KillDeathChart stats={stats} handlePlayerClick={handlePlayerClick}/>
    </>
  )
}
