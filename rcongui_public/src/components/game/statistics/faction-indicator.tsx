import React from 'react'
import {FactionEnum} from '@/types/player'
import {cn, getDarkTeamIconSrc, getLightTeamIconSrc} from '@/lib/utils'
import { useTheme } from '@/hooks/use-theme-provider'

type FactionIndicatorProps = {
  faction?: FactionEnum | null
} & React.HTMLAttributes<HTMLSpanElement>

export function FactionIndicator({ faction, ...props }: FactionIndicatorProps) {
  const theme = useTheme()
  const getTeamIconSrc = theme.theme === "dark" ? getLightTeamIconSrc : getDarkTeamIconSrc
  const commonStyle = 'inline-block w-4 size-5 rounded';
  if (faction) {
    return <img className={cn(commonStyle, props.className)} alt={faction} src={getTeamIconSrc(faction)} width={20} height={20} />
  }
  return null;
}
