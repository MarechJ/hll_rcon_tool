'use client';

import React from 'react';
import { Spinner } from '@shared/components/spinner';
import { useLiveGameStatsQuery } from '../utils/queries/live-game-stats';
import { DataTable } from '../components/game/live-table';
import { columns as liveColumns } from '../components/game/live-columns';
import { columns as faceoffColumns } from '../components/game/faceoff-columns';
import { useLivePageStore } from '../utils/stores/useLivePageStore';
import { SimpleTable } from '../components/game/simple-table';
import { mergeKillsDeaths } from '../components/game/utils';
import Image from 'next/image';
import { ScaleIcon, ZapIcon, HeartCrackIcon, SkullIcon } from 'lucide-react';
import { Weapon } from '../components/game/types';
import {
  deathByColumns,
  killByColumns,
} from '../components/game/weapons-columns';

// const scores = [
//   { key: "combat", label: "Combat", src: "/roles/score_combat.png" },
//   { key: "offense", label: "Offensive", src: "/roles/score_offensive.png" },
//   { key: "defense", label: "Defensive", src: "/roles/score_defensive.png" },
//   { key: "support", label: "Support", src: "/roles/score_support.png" },
// ] as const;

const scores = [
  { key: 'kill_death_ratio', label: 'K/D', icon: ScaleIcon },
  { key: 'kills_streak', label: 'Killstreak', icon: ZapIcon },
  { key: 'deaths_without_kill_streak', label: 'Deathstreak', icon: SkullIcon },
  { key: 'teamkills', label: 'Teamkills', icon: HeartCrackIcon },
] as const;

export default function LiveGameStats() {
  const [liveGameStats, { isFetching }] = useLiveGameStatsQuery();
  const playerId = useLivePageStore((state) => state.playerId);

  const player = React.useMemo(
    () => liveGameStats.stats.find((player) => player.player_id == playerId),
    [playerId]
  );

  const killsBy = player
    ? Object.entries(player.weapons).map((entry) => ({
        name: entry[0],
        count: entry[1],
      }))
    : [];
  killsBy.sort((a, b) => b.count - a.count);

  const deathsBy = player
    ? Object.entries(player.death_by_weapons).map((entry) => ({
        name: entry[0],
        count: entry[1],
      }))
    : [];
  deathsBy.sort((a, b) => b.count - a.count);

  return (
    <section id="live-game-statistics">
      <h2 className="sr-only">Live Statistics</h2>
      <div className="relative flex flex-col-reverse md:flex-row">
        <article className="w-full md:w-2/3">
          <DataTable columns={liveColumns} data={liveGameStats.stats} />
        </article>
        <aside className="w-full md:w-1/3 min-h-32">
          {player ? (
            <div className="divide-y-[1px] md:sticky md:top-14 border md:border-l-0">
              <h3 className="grid items-center text-xl text-center px-2 h-12">
                {player.player}
              </h3>
              <section className="flex flex-row justify-around h-[7.5rem]">
                {scores.map((score) => {
                  const Icon = score.icon;
                  return (
                    <IconStatistic stat={player[score.key]} text={score.label}>
                      <Icon size={20} />
                    </IconStatistic>
                  );
                })}
              </section>
              <SimpleTable
                columns={faceoffColumns}
                data={mergeKillsDeaths(player)}
              />
              <SimpleTable columns={killByColumns} data={killsBy} />
              <SimpleTable columns={deathByColumns} data={deathsBy} />
            </div>
          ) : (
            <div className="w-full px-10 py-5 text-center border md:border-l-0 md:sticky md:top-14">
              <div className="grid items-center border border-dashed w-full h-40 text-2xl">
                SELECT A PLAYER
              </div>
            </div>
          )}
        </aside>
      </div>
    </section>
  );
}

function IconStatistic({
  text,
  stat,
  children,
}: {
  text: string;
  stat: number;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col justify-center items-center divide-y-2 divide-foreground gap-1 p-2">
      <div className="flex flex-col items-center justify-center space-y-1">
        <span className="p-1 md:p-2 rounded-md">{children}</span>
        <span className="text-xs">{text}</span>
      </div>
      <span className="text-lg md:text-xl w-10 text-center font-semibold">
        {stat}
      </span>
    </div>
  );
}
