'use client';

import React from 'react';
import {
  ScaleIcon,
  ZapIcon,
  HeartCrackIcon,
  SkullIcon,
  ChevronsUpDownIcon,
  Gamepad2Icon,
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
import { SimpleIcon } from '@shared/components/simple-icon';
import { siSteam } from 'simple-icons';
import Link from 'next/link';

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
  isMobile,
}: {
  player: Player | PlayerWithStatus;
  isMobile?: boolean;
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
    <div className="divide-y pb-2 lg:sticky lg:top-14 border lg:border-l-0">
      {!isMobile && (
        <div className="flex justify-between items-center gap-1 px-2 h-12">
          <div className="flex justify-center items-center gap-2 grow">
            {isPlayerWithStatus(player) && player.is_online ? (
              <Status player={player} className="animate-ping" />
            ) : isPlayerWithStatus(player) ? (
              <Status player={player} />
            ) : null}
            <h3 className="text-xl text-center">{player.player}</h3>
          </div>
          <div className="flex flex-row justify-center items-center">
            <Button size={'icon'} variant={'outline'} asChild>
              {isSteamPlayer(player) ? (
                <Link
                  href={getSteamProfileUrl(player.player_id)}
                  target="_blank"
                >
                  <SimpleIcon
                    icon={siSteam}
                    size={20}
                    className="dark:fill-current"
                  />
                </Link>
              ) : (
                <Link href={getXboxProfileUrl(player.player)} target="_blank">
                  <Gamepad2Icon />
                </Link>
              )}
            </Button>
            {/* <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size={'xs'}
                  variant={'ghost'}
                  className="text-orange-400 hover:text-orange-600"
                >
                  <MessageSquareWarningIcon />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Report player</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider> */}
          </div>
        </div>
      )}
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
        <span className="p-1 lg:p-2 rounded-md">{children}</span>
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
        <Button
          variant="ghost"
          size="default"
          className="w-full justify-start rounded-none pl-1"
        >
          {name}
          <ChevronsUpDownIcon className="h-4 w-4" />
          <span className="sr-only">Toggle {name}</span>
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent>{children}</CollapsibleContent>
    </Collapsible>
  );
}

export function isSteamPlayer(player: Player) {
  const { player_id: id } = player;
  return id.length === 17 && !Number.isNaN(Number(id));
}

export function getSteamProfileUrl(id: string) {
  return `https://steamcommunity.com/profiles/${id}`;
}

export function getXboxProfileUrl(playerName: string) {
  return `https://xboxgamertag.com/search/${playerName}`;
}
