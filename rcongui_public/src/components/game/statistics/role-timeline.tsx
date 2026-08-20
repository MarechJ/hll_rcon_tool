import { HLL_ROLES, roleIcon } from '@/constants/roles'
import { PlayerUnit } from '@/types/player'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { useTranslation } from 'react-i18next'
import { SimpleWeaponType } from '@/types/weapon'
import { SIMPLE_WEAPON_TYPE_COLORS } from '@/constants/weapon-type-colors'

type RoleSegment = {
  role: number
  start: number
  end: number
}

const MINIMUM_ROLE_DURATION_SECONDS = 30

const ROLE_WEAPON_TYPES: Record<number, SimpleWeaponType> = {
  0: SimpleWeaponType.Infantry,
  1: SimpleWeaponType.Infantry,
  2: SimpleWeaponType.MachineGun,
  3: SimpleWeaponType.Infantry,
  4: SimpleWeaponType.Sniper,
  5: SimpleWeaponType.Infantry,
  6: SimpleWeaponType.MachineGun,
  7: SimpleWeaponType.Explosive,
  8: SimpleWeaponType.Explosive,
  9: SimpleWeaponType.Infantry,
  10: SimpleWeaponType.Sniper,
  11: SimpleWeaponType.Armor,
  12: SimpleWeaponType.Armor,
  13: SimpleWeaponType.Commander,
  14: SimpleWeaponType.Artillery,
  15: SimpleWeaponType.Artillery,
  16: SimpleWeaponType.Artillery,
}

function formatTime(seconds: number) {
  const minutes = Math.floor(Math.max(0, seconds) / 60)
  return `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`
}

function roleSegments(units: PlayerUnit[], gameDuration: number): RoleSegment[] {
  const orderedUnits = [...units].sort((a, b) => a.ts - b.ts)
  const segments: RoleSegment[] = []

  orderedUnits.forEach((unit, index) => {
    const isTeamLobbyDefault = unit.squad === -111 && unit.role === 0
    if (unit.team < 0 || isTeamLobbyDefault || unit.role < 0 || unit.role >= HLL_ROLES.length) return

    const start = Math.max(0, Math.min(unit.ts, gameDuration))
    const end = Math.max(start, Math.min(orderedUnits[index + 1]?.ts ?? gameDuration, gameDuration))
    if (end <= start) return

    const previous = segments[segments.length - 1]
    if (previous?.role === unit.role && previous.end === start) previous.end = end
    else segments.push({ role: unit.role, start, end })
  })

  return segments.filter((segment) => segment.end - segment.start >= MINIMUM_ROLE_DURATION_SECONDS)
}

export function RoleTimeline({ units, gameDuration }: { units: PlayerUnit[]; gameDuration: number }) {
  const { t } = useTranslation('game')
  const segments = roleSegments(units, gameDuration)

  if (!segments.length || gameDuration <= 0) return null

  return (
    <section className="space-y-1.5 px-3 py-2" aria-label={t('timelineDetails.roleTimeline')}>
      <div className="flex items-center justify-between text-[10px] text-muted-foreground">
        <span className="font-medium text-foreground">{t('timelineDetails.rolesLabel')}</span>
        <span>{formatTime(gameDuration)}</span>
      </div>
      <TooltipProvider>
        <div className="relative h-5 w-full overflow-hidden rounded-sm border border-border bg-transparent">
          {segments.map((segment, index) => {
            const icon = roleIcon(segment.role, 'black')
            const name = t(`timelineDetails.roles.${HLL_ROLES[segment.role]}`)
            const color = SIMPLE_WEAPON_TYPE_COLORS[ROLE_WEAPON_TYPES[segment.role]]

            return (
              <Tooltip key={`${segment.start}-${segment.end}-${segment.role}-${index}`}>
                <TooltipTrigger asChild>
                  <div
                    className="absolute inset-y-0 flex min-w-px items-center justify-center overflow-hidden border-x border-background/40"
                    style={{
                      left: `${(segment.start / gameDuration) * 100}%`,
                      width: `${((segment.end - segment.start) / gameDuration) * 100}%`,
                      backgroundColor: color,
                    }}
                    aria-label={t('timelineDetails.roleInterval', {
                      role: name,
                      start: formatTime(segment.start),
                      end: formatTime(segment.end),
                    })}
                  >
                    {icon && <img className="size-3.5 shrink-0 object-contain" src={icon} alt="" aria-hidden="true" />}
                  </div>
                </TooltipTrigger>
                <TooltipContent className="text-xs">
                  <div className="font-medium">{name}</div>
                  <div className="tabular-nums text-muted-foreground">
                    {formatTime(segment.start)}–{formatTime(segment.end)}
                  </div>
                </TooltipContent>
              </Tooltip>
            )
          })}
        </div>
      </TooltipProvider>
    </section>
  )
}
