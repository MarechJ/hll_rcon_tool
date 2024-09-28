'use client';

import React from 'react';
import {
  ScaleIcon,
  ZapIcon,
  HeartCrackIcon,
  SkullIcon,
  ChevronsUpDownIcon,
} from 'lucide-react';
import { mergeKillsDeaths } from './utils';
import { SimpleTable } from './simple-table';
import { deathByColumns, killByColumns } from './weapons-columns';
import { columns as faceoffColumns } from './faceoff-columns';
import { Player, PlayerWithStatus } from './types';
import { ScrollArea } from '@shared/components/ui/scroll-area';
import { Button } from '@shared/components/ui/button';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@shared/components/ui/collapsible';
import Image from 'next/image';
import { isPlayerWithStatus, Status } from './player-status';

const points = [
  { key: 'kills', label: 'K', icon: '/roles/infantry.png' },
  { key: 'deaths', label: 'D', icon: '/roles/medic.png' },
  { key: 'combat', label: 'C', icon: '/roles/score_combat.png' },
  { key: 'offense', label: 'O', icon: '/roles/score_offensive.png' },
  { key: 'defense', label: 'D', icon: '/roles/score_defensive.png' },
  { key: 'support', label: 'S', icon: '/roles/score_support.png' },
] as const;

const scores = [
  { key: 'kill_death_ratio', label: 'K/D', icon: ScaleIcon },
  { key: 'kills_streak', label: 'Killstreak', icon: ZapIcon },
  { key: 'deaths_without_kill_streak', label: 'Deathstreak', icon: SkullIcon },
  { key: 'teamkills', label: 'Teamkills', icon: HeartCrackIcon },
] as const;

export function PlayerGameDetail({
  player,
}: {
  player: Player | PlayerWithStatus;
}) {
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
    <div className="divide-y md:sticky md:top-14 border md:border-l-0 pb-2">
      <h3 className="flex justify-center items-center gap-2 text-xl text-center px-2 h-12">
        {isPlayerWithStatus(player) && player.is_online ? (
          <Status player={player} className="animate-ping" />
        ) : isPlayerWithStatus(player) ? (
          <Status player={player} />
        ) : null}{' '}
        {player.player}
      </h3>
      <ScrollArea className="h-player-detail">
        <div className="divide-y">
          <section className="flex flex-row divide-x justify-around h-10">
            {points.map((point) => (
              <div
                key={point.key}
                className="flex flex-col w-1/6 justify-center items-center"
              >
                <Image
                  src={point.icon}
                  width={12}
                  height={12}
                  alt={point.label}
                  className="mb-[2px] bg-primary dark:bg-transparent"
                />
                <div className="text-sm">{player[point.key]}</div>
              </div>
            ))}
          </section>
          <section className="flex flex-row justify-around h-20">
            {scores.map((score) => {
              const Icon = score.icon;
              return (
                <IconStatistic
                  key={score.key}
                  stat={player[score.key]}
                  text={score.label}
                >
                  <Icon size={16} />
                </IconStatistic>
              );
            })}
          </section>
          <CollapsibleSection name="Encounters" defaultOpen={true}>
            <SimpleTable
              columns={faceoffColumns}
              data={mergeKillsDeaths(player)}
            />
          </CollapsibleSection>
          <CollapsibleSection name="Kills by">
            <SimpleTable columns={killByColumns} data={killsBy} />
          </CollapsibleSection>
          <CollapsibleSection name="Deaths by">
            <SimpleTable columns={deathByColumns} data={deathsBy} />
          </CollapsibleSection>
        </div>
      </ScrollArea>
    </div>
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
    <div className="flex flex-col justify-center items-center divide-y divide-foreground gap-1 p-2">
      <div className="flex flex-col items-center justify-center space-y">
        <span className="p-1 md:p-2 rounded-md">{children}</span>
        <span className="text-xs">{text}</span>
      </div>
      <span className="w-10 text-center font-semibold">{stat}</span>
    </div>
  );
}

function CollapsibleSection({
  name,
  defaultOpen,
  children,
}: {
  name: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen ?? false);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger asChild>
        <Button variant="ghost" size="default" className="w-full justify-start rounded-none pl-1">
          {name}
          <ChevronsUpDownIcon className="h-4 w-4" />
          <span className="sr-only">Toggle {name}</span>
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent>{children}</CollapsibleContent>
    </Collapsible>
  );
}
