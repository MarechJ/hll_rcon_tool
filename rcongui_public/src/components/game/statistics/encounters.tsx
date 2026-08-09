import { HLL_ROLES, roleIcon } from '@/constants/roles'
import { Marker, MarkerContent } from '@/components/ui/marker'
import { GamePlayer } from '@/components/game/statistics/game-stats-container'
import { MatchScore } from '@/types/api'
import { KillInfo, Player, PlayerUnit } from '@/types/player'
import { Fragment } from 'react'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import { Trans, useTranslation } from 'react-i18next'

function formatTime(seconds: number) {
  const minutes = Math.floor(seconds / 60)
  return `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`
}

type StreakTitle = 'unstoppable' | 'impressive' | 'dominating' | 'killingSpree' | 'rampage'

const STREAK_TRANSLATION_KEYS: Record<StreakTitle, `timelineDetails.streak.titles.${StreakTitle}`> = {
  unstoppable: 'timelineDetails.streak.titles.unstoppable',
  impressive: 'timelineDetails.streak.titles.impressive',
  dominating: 'timelineDetails.streak.titles.dominating',
  killingSpree: 'timelineDetails.streak.titles.killingSpree',
  rampage: 'timelineDetails.streak.titles.rampage',
}

function streakTitle(count: number): StreakTitle | undefined {
  if (count >= 50) return 'unstoppable'
  if (count >= 30) return 'impressive'
  if (count >= 20) return 'dominating'
  if (count >= 10) return 'killingSpree'
  if (count >= 8) return 'rampage'
  return undefined
}

function unitAt(units: PlayerUnit[], timestamp: number) {
  return units.filter((unit) => unit.ts <= timestamp).sort((a, b) => b.ts - a.ts)[0]
}

function RoleIcon({ unit }: { unit?: PlayerUnit }) {
  const { t } = useTranslation('game')
  const icon = roleIcon(unit?.role)
  const lightModeIcon = roleIcon(unit?.role, 'black')
  const roleKey = unit?.role === undefined ? undefined : HLL_ROLES[unit.role]
  const role = roleKey ? t(`timelineDetails.roles.${roleKey}`) : t('timelineDetails.unknownRole')

  return icon && lightModeIcon ? (
    <span className="inline-flex size-4 shrink-0 items-center justify-center" title={role}>
      <img className="size-3.5 object-contain dark:hidden" src={lightModeIcon} alt={role} />
      <img className="hidden size-3.5 object-contain dark:block" src={icon} alt={role} />
    </span>
  ) : null
}

function EncounterItem({
  encounter,
  actorUnit,
  targetUnit,
  vehicleGroup,
  focusPlayerBy,
}: {
  encounter: KillInfo
  actorUnit?: PlayerUnit
  targetUnit?: PlayerUnit
  vehicleGroup?: VehicleGroupInfo
  focusPlayerBy?: ({ name, id }: { name?: string; id?: string }) => void
}) {
  const { t } = useTranslation('game')
  const isKill = encounter.action === 'KILL'

  return (
    <li
      className={`grid grid-cols-[2.25rem_minmax(0,1fr)] items-start gap-x-2 border-l-2 px-2 py-1.5 text-xs leading-5 @sm/timeline:gap-x-3 @md/timeline:grid-cols-[2.25rem_minmax(0,1fr)_minmax(0,max-content)] @lg/timeline:grid-cols-[2.5rem_minmax(0,1fr)_minmax(0,max-content)] ${
        isKill ? 'border-emerald-600 bg-emerald-500/[0.06]' : 'border-red-600 bg-red-500/[0.06]'
      } ${vehicleGroup ? 'border-r border-r-amber-500/50' : ''} ${
        vehicleGroup?.position === 0 ? 'rounded-tr-sm border-t border-t-amber-500/50' : ''
      } ${vehicleGroup && vehicleGroup.position === vehicleGroup.size - 1 ? 'rounded-br-sm border-b border-b-amber-500/50' : ''}`}
      aria-label={t(isKill ? 'timelineDetails.kill' : 'timelineDetails.death')}
    >
      <time
        className="col-start-1 row-start-1 text-[11px] tabular-nums text-muted-foreground"
        dateTime={`PT${encounter.ts}S`}
      >
        {formatTime(encounter.ts)}
      </time>
      <span className="col-start-2 row-start-1 flex min-w-0 flex-wrap items-center gap-x-1.5">
        <RoleIcon unit={actorUnit} />
        <span className="sr-only">{t(isKill ? 'timelineDetails.killed' : 'timelineDetails.wasKilledBy')}</span>
        {isKill ? (
          <ArrowRight className="size-3.5 shrink-0 text-emerald-700 dark:text-emerald-400" aria-hidden="true" />
        ) : (
          <ArrowLeft className="size-3.5 shrink-0 text-red-700 dark:text-red-400" aria-hidden="true" />
        )}
        <RoleIcon unit={targetUnit} />
        <button
          type="button"
          className="min-w-0 wrap-anywhere text-left font-semibold text-foreground underline-offset-2 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          onClick={() => focusPlayerBy?.({ id: encounter.player_id })}
        >
          {encounter.player_name}
        </button>
      </span>
      {encounter.weapon && (
        <span className="col-start-2 row-start-2 min-w-0 wrap-anywhere text-muted-foreground @md/timeline:col-start-3 @md/timeline:row-start-1 @md/timeline:w-max @md/timeline:max-w-48">
          <Trans
            t={t}
            i18nKey="timelineDetails.withWeapon"
            values={{ weapon: encounter.weapon }}
            components={{ weapon: <span className="font-medium text-foreground" /> }}
          />
        </span>
      )}
    </li>
  )
}

type CapturingTeam = 'allies' | 'axis'

type VehicleGroupInfo = {
  id: number
  anchor: number
  position: number
  size: number
}

type TimelineEntry =
  | {
      type: 'encounter'
      encounter: KillInfo
      encounterIndex: number
      vehicleGroup?: VehicleGroupInfo
      timestamp: number
    }
  | {
      type: 'cap-flip'
      flip: MatchScore
      capturedBy?: CapturingTeam
      capFlipIndex: number
      timestamp: number
    }
  | { type: 'player-state'; event: PlayerStateEvent; playerStateIndex: number; timestamp: number }

type TeamId = 1 | 2

type PlayerStateEvent =
  | { kind: 'joined'; timestamp: number; team: TeamId }
  | { kind: 'disconnected'; timestamp: number }
  | { kind: 'reconnected'; timestamp: number; team: TeamId; previousTeam: TeamId }
  | { kind: 'switched'; timestamp: number; team: TeamId; previousTeam: TeamId }

function isTeamId(team: number): team is TeamId {
  return team === 1 || team === 2
}

function playerStateEvents(units: PlayerUnit[]): PlayerStateEvent[] {
  const events: PlayerStateEvent[] = []
  let lastTeam: TeamId | undefined
  let hasJoined = false
  let isDisconnected = false
  const orderedUnits = [...units].sort((a, b) => a.ts - b.ts)

  orderedUnits.forEach((unit) => {
    const offline = unit.team === -111 && unit.squad === -111 && unit.role === -111

    if (offline) {
      if (hasJoined && !isDisconnected) events.push({ kind: 'disconnected', timestamp: unit.ts })
      isDisconnected = true
      return
    }

    // The default rifleman with no squad is a lobby placeholder. Other roles may
    // retain -111 after a deployed player is removed from their squad.
    if (unit.squad === -111 && unit.role === 0) return

    if (!isTeamId(unit.team)) return

    if (!hasJoined) {
      events.push({ kind: 'joined', timestamp: unit.ts, team: unit.team })
      hasJoined = true
    } else if (isDisconnected && lastTeam) {
      events.push({ kind: 'reconnected', timestamp: unit.ts, team: unit.team, previousTeam: lastTeam })
    } else if (lastTeam && unit.team !== lastTeam) {
      events.push({ kind: 'switched', timestamp: unit.ts, team: unit.team, previousTeam: lastTeam })
    }

    lastTeam = unit.team
    isDisconnected = false
  })

  return events
}

function PlayerStateMarker({ event, playerName }: { event: PlayerStateEvent; playerName: string }) {
  const { t } = useTranslation('game')
  const team = 'team' in event ? t(event.team === 1 ? 'allies' : 'axis') : undefined
  const previousTeam = 'previousTeam' in event ? t(event.previousTeam === 1 ? 'allies' : 'axis') : undefined
  const key =
    event.kind === 'joined'
      ? 'timelineDetails.playerState.joined'
      : event.kind === 'disconnected'
        ? 'timelineDetails.playerState.disconnected'
        : event.kind === 'switched'
          ? 'timelineDetails.playerState.switched'
          : event.team !== event.previousTeam
            ? 'timelineDetails.playerState.reconnectedAfterSwitch'
            : 'timelineDetails.playerState.reconnected'

  return (
    <li className="px-2 py-1">
      <Marker variant="separator" className="text-xs">
        <MarkerContent>
          <time className="tabular-nums" dateTime={`PT${event.timestamp}S`}>
            {formatTime(event.timestamp)}
          </time>{' '}
          <Trans
            t={t}
            i18nKey={key}
            values={{ player: playerName, team, previousTeam }}
            components={{
              player: <span className="font-semibold text-foreground" />,
              team: <span className="font-medium text-foreground" />,
              previousTeam: <span className="font-medium text-foreground" />,
            }}
          />
        </MarkerContent>
      </Marker>
    </li>
  )
}

export function Encounters({
  player,
  focusPlayerBy,
  players = [],
  capFlips = [],
}: {
  player: Player
  focusPlayerBy?: ({ name, id }: { name?: string; id?: string }) => void
  players?: GamePlayer[]
  capFlips?: MatchScore[]
}) {
  const { t } = useTranslation('game')
  const encounters = 'encounters' in player && player.encounters ? player.encounters : []
  const units = 'units' in player && player.units ? player.units : []
  const stateEvents = playerStateEvents(units)
  const vehicleGroups = new Map<number, VehicleGroupInfo>()
  const tankCrewKillsByTimestamp = new Map<number, number[]>()

  if (player.vehicles_destroyed > 0) {
    encounters.forEach((encounter, encounterIndex) => {
      if (encounter.action !== 'KILL') return
      const targetUnits = players.find(({ id }) => id === encounter.player_id)?.units ?? []
      const targetRole = unitAt(targetUnits, encounter.ts)?.role
      if (targetRole !== 11 && targetRole !== 12) return

      const indices = tankCrewKillsByTimestamp.get(encounter.ts) ?? []
      indices.push(encounterIndex)
      tankCrewKillsByTimestamp.set(encounter.ts, indices)
    })

    Array.from(tankCrewKillsByTimestamp.entries())
      .filter(([, encounterIndices]) => encounterIndices.length >= 2 && encounterIndices.length <= 3)
      .sort(([a], [b]) => a - b)
      .slice(0, player.vehicles_destroyed)
      .forEach(([, encounterIndices], id) => {
        const anchor = Math.min(...encounterIndices)
        encounterIndices.forEach((encounterIndex, position) => {
          vehicleGroups.set(encounterIndex, { id, anchor, position, size: encounterIndices.length })
        })
      })
  }

  const firstJoinedAt = stateEvents.find((event) => event.kind === 'joined')?.timestamp
  const orderedCapFlips = [...capFlips].sort((a, b) => a.ts - b.ts)
  const capFlipEntries = orderedCapFlips
    .map((flip, capFlipIndex) => {
      const previous = orderedCapFlips[capFlipIndex - 1]
      const capturedBy = previous
        ? flip.allied_score > previous.allied_score
          ? ('allies' as const)
          : flip.axis_score > previous.axis_score
            ? ('axis' as const)
            : undefined
        : undefined

      return {
        type: 'cap-flip' as const,
        flip,
        capturedBy,
        capFlipIndex,
        timestamp: flip.ts,
      }
    })
    .filter(({ capFlipIndex, timestamp }) => {
      return capFlipIndex > 0 && firstJoinedAt !== undefined && timestamp >= firstJoinedAt
    })
  const streakStarts = new Map<number, StreakTitle>()
  const streakEnds = new Map<number, number>()

  for (let start = 0; start < encounters.length; ) {
    if (encounters[start].action !== 'KILL') {
      start += 1
      continue
    }

    let end = start
    while (end + 1 < encounters.length && encounters[end + 1].action === 'KILL') end += 1

    const count = end - start + 1
    const title = streakTitle(count)
    if (title) streakStarts.set(start, title)
    if (title && encounters[end + 1]?.action === 'DEATH') streakEnds.set(end + 1, count)
    start = end + 1
  }

  const timeline: TimelineEntry[] = [
    ...encounters.map((encounter, encounterIndex) => ({
      type: 'encounter' as const,
      encounter,
      encounterIndex,
      vehicleGroup: vehicleGroups.get(encounterIndex),
      timestamp: encounter.ts,
    })),
    ...capFlipEntries,
    ...stateEvents.map((event, playerStateIndex) => ({
      type: 'player-state' as const,
      event,
      playerStateIndex,
      timestamp: event.timestamp,
    })),
  ].sort((a, b) => {
    const timeDifference = a.timestamp - b.timestamp
    if (timeDifference) return timeDifference
    const typeOrder = { 'player-state': 0, 'cap-flip': 1, encounter: 2 }
    const typeDifference = typeOrder[a.type] - typeOrder[b.type]
    if (typeDifference) return typeDifference
    if (a.type === 'encounter' && b.type === 'encounter') {
      const aOrder = a.vehicleGroup ? a.vehicleGroup.anchor + a.vehicleGroup.position / 10 : a.encounterIndex
      const bOrder = b.vehicleGroup ? b.vehicleGroup.anchor + b.vehicleGroup.position / 10 : b.encounterIndex
      return aOrder - bOrder
    }
    if (a.type === 'cap-flip' && b.type === 'cap-flip') return a.capFlipIndex - b.capFlipIndex
    if (a.type === 'player-state' && b.type === 'player-state') return a.playerStateIndex - b.playerStateIndex
    return 0
  })

  return (
    <ol
      className="@container/timeline flex w-full list-none flex-col overflow-y-auto py-2 pr-1"
      aria-label={t('timelineDetails.encountersTimeline')}
    >
      {timeline.map((entry) => {
        if (entry.type === 'player-state') {
          return (
            <PlayerStateMarker
              key={`player-state-${entry.timestamp}-${entry.playerStateIndex}`}
              event={entry.event}
              playerName={player.player}
            />
          )
        }

        if (entry.type === 'cap-flip') {
          const playerTeam = unitAt(units, entry.timestamp)?.team
          const capturedTeamId = entry.capturedBy === 'allies' ? 1 : entry.capturedBy === 'axis' ? 2 : undefined
          const captureDescription = capturedTeamId
            ? playerTeam === capturedTeamId
              ? t('timelineDetails.capFlip.playerTeamCaptured', { player: player.player })
              : isTeamId(playerTeam)
                ? t('timelineDetails.capFlip.playerTeamLost', { player: player.player })
                : t('timelineDetails.capFlip.teamCaptured', {
                    team: t(capturedTeamId === 1 ? 'allies' : 'axis'),
                  })
            : t('timelineDetails.capFlip.score')

          return (
            <li key={`cap-flip-${entry.timestamp}-${entry.capFlipIndex}`} className="px-2 py-1">
              <Marker variant="separator" className="text-xs">
                <MarkerContent className="min-w-0 flex-1 whitespace-normal wrap-anywhere">
                  <span className="block font-semibold text-foreground">
                    <time className="tabular-nums" dateTime={`PT${entry.timestamp}S`}>
                      {formatTime(entry.timestamp)}
                    </time>{' '}
                    {captureDescription}
                  </span>
                  <span className="mt-0.5 block font-medium text-foreground">
                    {t('timelineDetails.capFlip.scoreLine', {
                      allies: t('allies'),
                      alliedScore: entry.flip.allied_score,
                      axisScore: entry.flip.axis_score,
                      axis: t('axis'),
                    })}
                  </span>
                </MarkerContent>
              </Marker>
            </li>
          )
        }

        const { encounter, encounterIndex } = entry
        const actorUnit = unitAt(units, encounter.ts)
        const targetUnits = players.find(({ id }) => id === encounter.player_id)?.units ?? []
        const title = streakStarts.get(encounterIndex)
        const endedCount = streakEnds.get(encounterIndex)
        const vehicleGroup = entry.vehicleGroup

        return (
          <Fragment key={`encounter-${encounter.ts}-${encounter.action}-${encounter.player_id}-${encounterIndex}`}>
            {title && (
              <li className="px-2 py-1">
                <Marker variant="separator" className="text-xs text-amber-700 dark:text-amber-400">
                  <MarkerContent>
                    {t('timelineDetails.streak.title', {
                      player: player.player,
                      title: t(STREAK_TRANSLATION_KEYS[title]),
                    })}
                  </MarkerContent>
                </Marker>
              </li>
            )}
            {vehicleGroup?.position === 0 && (
              <li className="px-2 py-1">
                <Marker variant="separator" className="text-xs text-amber-700 dark:text-amber-400">
                  <MarkerContent className="font-semibold">
                    {t('timelineDetails.tankDestroyed', { player: player.player })}
                  </MarkerContent>
                </Marker>
              </li>
            )}
            {endedCount && (
              <li className="px-2 py-1">
                <Marker variant="separator" className="text-xs text-amber-700 dark:text-amber-400">
                  <MarkerContent>
                    {t('timelineDetails.streak.ended', { player: player.player, count: endedCount })}
                  </MarkerContent>
                </Marker>
              </li>
            )}
            <EncounterItem
              encounter={encounter}
              actorUnit={actorUnit}
              targetUnit={unitAt(targetUnits, encounter.ts)}
              vehicleGroup={vehicleGroup}
              focusPlayerBy={focusPlayerBy}
            />
          </Fragment>
        )
      })}
    </ol>
  )
}
