import React from "react";
import {ResponsiveContainer, Tooltip, TooltipProps, Treemap} from "recharts";
import {getColorForTeam} from "@/components/game/statistics/utils";
import {Player, PlayerBase, PlayerWithStatus, TeamEnum} from "@/types/player";
import {WeaponType} from "@/types/weapon";
import {useTranslation} from "react-i18next";
import {NameType, ValueType} from "recharts/types/component/DefaultTooltipContent";
import {TreemapNode} from "recharts/types/util/types";

export const KillCategoryChart = ({stats, handlePlayerClick}: {
  stats: Player[] | PlayerWithStatus[]
  handlePlayerClick: (id: string) => void
}) => {

  const axisPlayers = stats.filter(player => player.team.side === TeamEnum.AXIS).sort((a, b) => b.kills - a.kills);
  const alliesPlayers = stats.filter(player => player.team.side === TeamEnum.ALLIES).sort((a, b) => b.kills - a.kills);

  const displayedTypes = [WeaponType.Infantry, WeaponType.MachineGun, WeaponType.Artillery, WeaponType.Armor, WeaponType.Sniper, WeaponType.Commander, WeaponType.Grenade, WeaponType.Bazooka, WeaponType.Satchel, WeaponType.Mine, WeaponType.PAK]

  return (
    <>
      {displayedTypes.map(type => <KillTreemapChart key={type} axisPlayers={axisPlayers} alliesPlayers={alliesPlayers} type={type}
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

  const handleClick = (node: TreemapNode)  => {
    handlePlayerClick(node.player.player_id);
  }

  return (
    <div className="py-4">
      <h2 className="text-xl text-center">{t(`weaponType.${type}`)}</h2>
      <h5 className="text-center">({alliesKills} vs {axisKills})</h5>
      <div className={"w-full flex relative mt-2"} style={{height: `calc(100vh * ${totalKills}/5000`, minHeight: '5px'}}>
        <div className={"absolute border w-[0] h-full left-1/2 border-purple-600 z-20 pointer-events-none"}/>
        <ResponsiveContainer width={(alliesKills / totalKills * 99) + "%"} height="100%">
          <Treemap width={400} height={200} data={alliesData} nameKey={"player"} dataKey={"kills"} stroke="#fff" isAnimationActive={false}
                   fill={getColorForTeam(TeamEnum.ALLIES)} onClick={handleClick} content={<CustomizedContent mirrored/>}>
            <Tooltip content={<CustomTooltip/>}/>
          </Treemap>
        </ResponsiveContainer>
        <ResponsiveContainer width={(axisKills / totalKills * 99) + "%"} height="100%">
          <Treemap width={400} height={200} data={axisData} dataKey={"kills"} stroke="#fff" isAnimationActive={false}
                   fill={getColorForTeam(TeamEnum.AXIS)} onClick={handleClick} content={<CustomizedContent/>}>
            <Tooltip content={<CustomTooltip/>}/>
          </Treemap>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const CustomizedContent = ({ root, x, y, width, height, fill, index, value, mirrored }: any) => {
  const adjustedX = mirrored ? (root.width - (x + width)) : x

  return (
    <g>
      <rect
        x={adjustedX}
        y={y}
        width={width}
        height={height}
        fill={fill}
        className="cursor-pointer hover:opacity-80 transition-opacity"
      />
      {index < 10 && width > 50 && height > 30 && (
        <text
          x={adjustedX + width / 2}
          y={y + height / 2}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="#fff"
          fontSize={16}
          className="select-none pointer-events-none"
        >
          {index + 1}
        </text>
      )}
    </g>
  );
};

const CustomTooltip = ({
                         active,
                         payload,
                       }: TooltipProps<ValueType, NameType>) =>
{
  if (active && payload && payload.length) {
    return (
      <div className="bg-background border p-2">
        <span>{payload[0].payload.player.player}: </span>
        <span>{payload[0].payload.value}</span>
      </div>
    );
  }

  return null;
};
