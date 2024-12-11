import React from 'react'
import { PlayerWithStatus } from '@/types/player'
import { cn } from '@/lib/utils'

type StatusProps = {
  player: PlayerWithStatus
} & React.HTMLAttributes<HTMLSpanElement>

export function Status({ player, ...props }: StatusProps) {
  if (player.is_online) {
    return <span className={cn('w-4 size-2 rounded bg-green-600', props.className)}></span>
  }
  return <span className={cn('w-4 size-2 rounded bg-red-800', props.className)}></span>
}
