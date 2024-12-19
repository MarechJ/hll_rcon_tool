'use client'

import {useMemo, useState} from 'react'
import {DataTable} from './game-table'
import {Player, PlayerWithStatus, TeamEnum} from '@/types/player'
import useMediaQuery from '@/hooks/use-media-query'
import {ColumnDef} from '@tanstack/react-table'
import PlayerGameDetail from './player'
import {MobilePlayerGameDetail, NoPlayerGameDetail} from './player-detail'
import {
  ALL_GB_ArmorWeapon,
  ALL_GB_Weapon,
  ALL_GER_ArmorWeapon,
  ALL_GER_Weapon,
  ALL_RUS_ArmorWeapon,
  ALL_RUS_Weapon,
  ALL_US_ArmorWeapon,
  ALL_US_Weapon,
  GB_ArmorWeapon,
  GB_Weapon,
  GER_ArmorWeapon,
  GER_Weapon,
  RUS_ArmorWeapon,
  RUS_Weapon,
  US_ArmorWeapon,
  US_Weapon,
  Weapon
} from "@/types/weapon";
import {Route, Routes} from "react-router";
import {TeamStats} from "@/components/game/statistics/team/team-stats";

export default function GameStats({
  stats,
  getColumns,
  gameId,
  live,
}: {
  stats: Player[] | PlayerWithStatus[]
  getColumns: (handlePlayerClick: (id: string) => void) => ColumnDef<Player | PlayerWithStatus>[]
  gameId: string
  live: boolean
}) {
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | undefined>()
  const [openDrawer, setOpenDrawer] = useState<boolean>(false)
  const isSmallScreen = useMediaQuery('screen and (max-width: 1023px)')

  const handlePlayerClick = (id: string) => {
    setSelectedPlayerId(id)
    setOpenDrawer(true)
  }

  const selectedPlayer = useMemo(
    () => stats.find((player) => player.player_id === selectedPlayerId),
    [stats, selectedPlayerId],
  )

  const calcTeam = (kills: number, weapons: Record<Weapon, number>): TeamEnum  => {
    const threshold = 0.8;
    let adjustedKills = kills;
    let axisKills = 0;
    let alliesKills = 0;
    const weaponsSorted = Object.entries(weapons).sort(([nameA, countA], [nameB, countB]) => countB - countA);
    for (const [name, count] of weaponsSorted) {
      // don't count these weapons as those are both allies and axis weapon
      if (['SATCHEL', 'BOMBING RUN', 'STRAFING RUN', 'PRECISION STRIKE'].includes(name.toUpperCase())) {
        adjustedKills -= count;
      } else if (ALL_GER_Weapon.includes(name as GER_Weapon) || ALL_GER_ArmorWeapon.includes(name as GER_ArmorWeapon)) {
        axisKills += count;
      } else if (
        ALL_US_Weapon.includes(name as US_Weapon) || ALL_US_ArmorWeapon.includes(name as US_ArmorWeapon) ||
        ALL_RUS_Weapon.includes(name as RUS_Weapon) || ALL_RUS_ArmorWeapon.includes(name as RUS_ArmorWeapon) ||
        ALL_GB_Weapon.includes(name as GB_Weapon) || ALL_GB_ArmorWeapon.includes(name as GB_ArmorWeapon)
      ) {
        alliesKills += count;
      }
      if (axisKills >= adjustedKills * threshold) {
        return TeamEnum.AXIS;
      }
      if (alliesKills >= adjustedKills * threshold) {
        return TeamEnum.ALLIES;
      }
    }
    if (axisKills > 0 && alliesKills > 0) {
      return TeamEnum.MIXED;
    }
    return TeamEnum.UNKNOWN;
  }

  const statsWithTeam: Player[] | null = useMemo(
    () => live ? null : stats.map(player => {
      return {...player, team: calcTeam(player.kills, player.weapons)}
    }),
    [stats]
  );

  return (
    <section id={`game-statistics-${gameId}`}>
      <h2 className="sr-only">End of game statistics</h2>
      <div className="relative flex flex-col-reverse lg:flex-row">
        <article className="w-full lg:w-2/3">
          <Routes>
            <Route index element={<DataTable columns={getColumns(handlePlayerClick)} data={statsWithTeam ?? stats} tableId={gameId} />} />
            <Route path={"charts"} element={<TeamStats stats={statsWithTeam ?? []} handlePlayerClick={handlePlayerClick}/>} />
          </Routes>
        </article>
        <aside className="hidden w-full lg:block lg:w-1/3 min-h-32">
          {selectedPlayer ? <PlayerGameDetail player={selectedPlayer} /> : <NoPlayerGameDetail />}
        </aside>
      </div>
      {isSmallScreen && selectedPlayer && (
        <MobilePlayerGameDetail open={openDrawer} setOpen={setOpenDrawer} player={selectedPlayer} />
      )}
    </section>
  )
}
