import { ScaleIcon, ZapIcon, HeartCrackIcon, SkullIcon } from 'lucide-react';
import { mergeKillsDeaths } from './utils';
import { SimpleTable } from './simple-table';
import {
    deathByColumns,
    killByColumns,
  } from './weapons-columns';
import { columns as faceoffColumns } from './faceoff-columns';
import { Player } from './types';

const scores = [
    { key: 'kill_death_ratio', label: 'K/D', icon: ScaleIcon },
    { key: 'kills_streak', label: 'Killstreak', icon: ZapIcon },
    { key: 'deaths_without_kill_streak', label: 'Deathstreak', icon: SkullIcon },
    { key: 'teamkills', label: 'Teamkills', icon: HeartCrackIcon },
  ] as const;

export function PlayerGameDetail({ player } : { player: Player }) {
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
    )
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