import React from 'react'
import {FactionEnum} from '@/types/player'
import {cn} from '@/lib/utils'

type FactionIndicatorProps = {
  faction?: FactionEnum | null
} & React.HTMLAttributes<HTMLSpanElement>

export function FactionIndicator({ faction, ...props }: FactionIndicatorProps) {
  const commonStyle = 'inline-block w-4 size-5 rounded';
  if (faction === FactionEnum.CW) {
    return <img className={cn(commonStyle, props.className)} alt={faction} src={"/icons/teams/gb.webp"} width={20} height={20} />
  } else if (faction === FactionEnum.GB) {
    return <img className={cn(commonStyle, props.className)} alt={faction} src={"/icons/teams/gb.webp"} width={20} height={20} />
  } else if (faction === FactionEnum.GER) {
    return <img className={cn(commonStyle, props.className)} alt={faction} src={"/icons/teams/ger.webp"} width={20} height={20} />
  } else if (faction === FactionEnum.RUS) {
    return <img className={cn(commonStyle, props.className)} alt={faction} src={"/icons/teams/rus.webp"} width={20} height={20} />
  } else if (faction === FactionEnum.US) {
    return <img className={cn(commonStyle, props.className)} alt={faction} src={"/icons/teams/us.webp"} width={20} height={20} />
  }
  return null;
}
