import React from 'react'
import {TeamEnum} from '@/types/player'
import {cn} from '@/lib/utils'

type TeamIndicatorProps = {
  team?: TeamEnum
} & React.HTMLAttributes<HTMLSpanElement>

export function TeamIndicator({ team, ...props }: TeamIndicatorProps) {
  if (team === TeamEnum.AXIS) {
    return <span className={cn('w-4 size-2 rounded bg-red-600', props.className)}></span>
  } else if (team === TeamEnum.ALLIES) {
    return <span className={cn('w-4 size-2 rounded bg-blue-600', props.className)}></span>
  } else if (team === TeamEnum.MIXED) {
    return <span className={cn('w-4 size-2 rounded bg-yellow-400', props.className)}></span>
  } else if (team === TeamEnum.UNKNOWN) {
    return <span className={cn('w-4 size-2 rounded bg-gray-500', props.className)}></span>
  }
  return null;
}
