import React from 'react';
import { Player, PlayerWithStatus } from './types';
import { cn } from '@shared/utils';

export function isPlayerWithStatus(
  player: Player | PlayerWithStatus
): player is PlayerWithStatus {
  return (player as PlayerWithStatus).is_online !== undefined;
}

type StatusProps = {
    player: PlayerWithStatus
} & React.HTMLAttributes<HTMLSpanElement>

export function Status({ player, ...props } : StatusProps) {
  if (player.is_online) {
    return <span className={cn("size-2 rounded bg-green-600", props.className)}></span>;
  }
  return <span className={cn("size-2 rounded bg-red-800", props.className)}></span>;
}
