import React from "react";
import {ResponsiveContainer, Treemap} from "recharts";
import {getColorForTeam} from "@/components/game/statistics/utils";
import {Player, PlayerBase, PlayerWithStatus, TeamEnum} from "@/types/player";
import {WeaponType} from "@/types/weapon";
import {useTranslation} from "react-i18next";

export const KillCategoryChart = ({stats, handlePlayerClick}: {
  stats: Player[] | PlayerWithStatus[]
  handlePlayerClick: (id: string) => void
}) => {

  const axisPlayers = stats.filter(player => player.team.side === TeamEnum.AXIS).sort((a, b) => b.kills - a.kills);
  const alliesPlayers = stats.filter(player => player.team.side === TeamEnum.ALLIES).sort((a, b) => b.kills - a.kills);

  const displayedTypes = [WeaponType.Infantry, WeaponType.MachineGun, WeaponType.Artillery, WeaponType.Armor, WeaponType.Sniper, WeaponType.Commander, WeaponType.Grenade, WeaponType.Bazooka, WeaponType.Satchel, WeaponType.Mine, WeaponType.PAK]

  return (
    <>
      {displayedTypes.map(type => <KillTreemapChart axisPlayers={axisPlayers} alliesPlayers={alliesPlayers} type={type}
                          handlePlayerClick={handlePlayerClick}/>)}
    </>
  );
};


const KillTreemapChart = ({axisPlayers, alliesPlayers, type, handlePlayerClick }: {
  axisPlayers: PlayerBase[],
  alliesPlayers: PlayerBase[],
  type: WeaponType,
  handlePlayerClick: (id: string) => void,
}) => {
  const {t} = useTranslation("game");

  const axisData = axisPlayers.map(player => ({ player: player, kills: player.kills_by_type[type] })).filter(player => player.kills).sort((a, b) => b.kills - a.kills);
  const alliesData = alliesPlayers.map(player => ({ player: player, kills: player.kills_by_type[type] })).filter(player => player.kills).sort((a, b) => b.kills - a.kills);

  const axisKills = axisData.reduce((prev, player) => prev + player.kills, 0);
  const alliesKills = alliesData.reduce((prev, player) => prev + player.kills, 0);
  const totalKills = axisKills + alliesKills;

  return (
    <div className="py-4">
      <h2 className="text-xl text-center">{t(`weaponType.${type}`)}</h2>
      <h2 className="text-xl text-center">({alliesKills} vs {axisKills})</h2>
      <div className={"w-full flex relative"} style={{height: `calc(100vh * ${totalKills}/5000`, minHeight: '5px'}}>
        <div className={"absolute border w-[0] h-full left-1/2 border-purple-600 z-20 pointer-events-none"}/>
        <ResponsiveContainer width={(alliesKills / totalKills * 99) + "%"} height="100%">
          <Treemap width={400} height={200} data={alliesData} nameKey={"player"} dataKey={"kills"} stroke="#fff"
                   fill={getColorForTeam(TeamEnum.ALLIES)}/>
        </ResponsiveContainer>
        <ResponsiveContainer width={(axisKills / totalKills * 99) + "%"} height="100%">
          <Treemap width={400} height={200} data={axisData} dataKey={"kills"} stroke="#fff"
                   fill={getColorForTeam(TeamEnum.AXIS)} onClick={node => handlePlayerClick(node.player_id)}/>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
