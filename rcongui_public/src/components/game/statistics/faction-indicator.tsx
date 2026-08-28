import React from 'react'
import { FactionEnum, StatusEnum } from '@/types/player'
import { cn } from '@/lib/utils'
import { Faction, getDarkFactionIconSrc, getLightFactionIconSrc } from '@/constants/factions'
import { useTheme } from '@/hooks/use-theme-provider'
import { Avatar, AvatarBadge, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

type FactionIndicatorProps = {
  faction?: Faction | null
  status?: StatusEnum | null
} & React.HTMLAttributes<HTMLSpanElement>

export function FactionIndicator({ faction, status, className, ...props }: FactionIndicatorProps) {
  const theme = useTheme()
  const getFactionIconSrc = theme.theme === 'dark' ? getLightFactionIconSrc : getDarkFactionIconSrc
  return (
    <Avatar size="sm" className={cn('overflow-visible', className)} {...props}>
      {faction && (<AvatarImage
        className="rounded-full"
        src={getFactionIconSrc(faction)}
        width={20}
        height={20}
        alt={faction ?? "lobby"}
      />)}
      <AvatarFallback></AvatarFallback>
      {status !== undefined &&
        (status === StatusEnum.ONLINE ? (
          <AvatarBadge className="bg-green-800 dark:bg-green-600" />
        ) : (
          <AvatarBadge className="bg-red-800 dark:bg-red-600" />
        ))}
    </Avatar>
  )
}
