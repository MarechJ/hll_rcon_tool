import React from 'react'
import { FactionEnum, StatusEnum } from '@/types/player'
import { cn, getDarkTeamIconSrc, getLightTeamIconSrc } from '@/lib/utils'
import { useTheme } from '@/hooks/use-theme-provider'
import { BotIcon } from 'lucide-react'
import { Avatar, AvatarBadge, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

type FactionIndicatorProps = {
  faction?: FactionEnum | null
  status?: StatusEnum | null
} & React.HTMLAttributes<HTMLSpanElement>

export function FactionIndicator({ faction, status, className, ...props }: FactionIndicatorProps) {
  const theme = useTheme()
  const getTeamIconSrc = theme.theme === 'dark' ? getLightTeamIconSrc : getDarkTeamIconSrc
  return (
    <Avatar size="sm" className={cn('overflow-visible', className)} {...props}>
      <AvatarImage
        className="rounded-full"
        src={getTeamIconSrc(faction ?? "lobby")}
        width={20}
        height={20}
        alt={faction ?? "lobby"}
      />
      <AvatarFallback></AvatarFallback>
      {status && status == StatusEnum.ONLINE ? (
        <AvatarBadge className="bg-green-800 dark:bg-green-600" />
      ) : (
        <AvatarBadge className="bg-red-800 dark:bg-red-600" />
      )}
    </Avatar>
  )
}
