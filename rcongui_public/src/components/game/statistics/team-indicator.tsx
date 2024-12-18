import React from 'react'
import {Player, PlayerWithStatus} from '@/types/player'
import { cn } from '@/lib/utils'

type TeamIndicatorProps = {
  player: Player
} & React.HTMLAttributes<HTMLSpanElement>

export function TeamIndicator({ player, ...props }: TeamIndicatorProps) {
  if (player.team === 'axis') {
    return <span className={cn('w-4 size-2 rounded bg-red-600', props.className)}></span>
  } else if (player.team === 'allies') {
    return <span className={cn('w-4 size-2 rounded bg-blue-600', props.className)}></span>
  } else if (player.team === 'mixed') {
    return <span className={cn('w-4 size-2 rounded bg-yellow-400', props.className)}></span>
  } else if (player.team === 'unknown') {
    return <span className={cn('w-4 size-2 rounded bg-gray-500', props.className)}></span>
  }
  return null;
}
