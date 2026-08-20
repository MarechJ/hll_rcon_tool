import { Gamepad2Icon } from 'lucide-react'
import { siEpicgames, siPlaystation, siSteam } from 'simple-icons'
import { Button } from '@/components/ui/button'
import { SimpleIcon } from '@/components/simple-icon'
import { Player } from '@/types/player'
import { getPlatformLabel, getPlatformProfileUrl, normalizePlatform, PLATFORMS } from '@/constants/platforms'

function PlatformIcon({ platform }: { platform?: string | null }) {
  switch (normalizePlatform(platform)) {
    case PLATFORMS.STEAM:
      return <SimpleIcon icon={siSteam} size={20} className="dark:fill-current" />
    case PLATFORMS.EPIC:
      return <SimpleIcon icon={siEpicgames} size={20} className="dark:fill-current" />
    case PLATFORMS.PLAYSTATION_NETWORK:
    case PLATFORMS.PLAYSTATION_5:
      return <SimpleIcon icon={siPlaystation} size={20} className="dark:fill-current" />
    default:
      return <Gamepad2Icon />
  }
}

export function PlatformLink({ player }: { player: Player }) {
  const label = getPlatformLabel(player.platform)
  const profileUrl = getPlatformProfileUrl(player.platform, player.player_id, player.player)

  if (!profileUrl) {
    return (
      <Button type="button" size="icon" variant="outline" title={label} aria-label={label} disabled>
        <PlatformIcon platform={player.platform} />
      </Button>
    )
  }

  return (
    <Button size="icon" variant="outline" asChild>
      <a href={profileUrl} target="_blank" rel="noreferrer" title={label} aria-label={label}>
        <PlatformIcon platform={player.platform} />
      </a>
    </Button>
  )
}
