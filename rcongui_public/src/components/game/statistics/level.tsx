import React from 'react'
import {cn} from '@/lib/utils'
import { getPlayerTier } from './utils'
import { useTheme } from '@/hooks/use-theme-provider'

type LevelProps = {
  level: number
} & React.HTMLAttributes<HTMLSpanElement>

export function Level({ level, ...props }: LevelProps) {
  const theme = useTheme()

  if (level < 1) {
    return null
  }

  const tier = getPlayerTier(level)

  if (tier === "Novice") {
    return <span className={cn(theme.theme === 'light' ? 'text-red-700' : 'text-red-500', props.className)}>{level}</span>
  } else if (tier === "Apprentice") {
    return <span className={cn(theme.theme === 'light' ? 'text-yellow-800' : 'text-yellow-500', props.className)}>{level}</span>
  } else if (tier === "Expert") {
    return <span className={cn(theme.theme === 'light' ? 'text-green-700' : 'text-green-500', props.className)}>{level}</span>
  } else if (tier === "Master") {
    return <span className={cn(theme.theme === 'light' ? 'text-blue-700' : 'text-blue-500', props.className)}>{level}</span>
  } else {
    return <span className={cn(theme.theme === 'light' ? 'text-purple-700' : 'text-purple-500', props.className)}>{level}</span>
  }
}
