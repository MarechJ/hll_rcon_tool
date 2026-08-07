import { roleIcon, roleName } from '@/constants/roles'
import { Marker, MarkerContent } from '@/components/ui/marker'
import { GamePlayer } from '@/components/game/statistics/game-stats-container'
import { MatchScore } from '@/types/api'
import { KillInfo, Player, PlayerUnit } from '@/types/player'
import { Fragment, type ReactNode } from 'react'
import { ArrowLeft, ArrowRight } from 'lucide-react'

function formatTime(seconds: number) {
  const minutes = Math.floor(seconds / 60)
  return `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`
}

function streakTitle(count: number) {
  if (count >= 50) return 'Unstoppable'
  if (count >= 30) return 'Impressive'
  if (count >= 20) return 'Dominating'
  if (count >= 10) return 'Killing spree'
  if (count >= 8) return 'Rampage'
  return undefined
}

function unitAt(units: PlayerUnit[], timestamp: number) {
  return units.filter((unit) => unit.ts <= timestamp).sort((a, b) => b.ts - a.ts)[0]
}

function RoleIcon({ unit }: { unit?: PlayerUnit }) {
  const icon = roleIcon(unit?.r)
  const lightModeIcon = roleIcon(unit?.r, 'black')
  const role = roleName(unit?.r)

  return icon && lightModeIcon ? (
    <span className="inline-flex size-4 shrink-0 items-center justify-center" title={role}>
      <img className="size-3.5 object-contain dark:hidden" src={lightModeIcon} alt={role ?? 'Unknown role'} />
      <img className="hidden size-3.5 object-contain dark:block" src={icon} alt={role ?? 'Unknown role'} />
    </span>
  ) : null
}

function EncounterItem({
  encounter,
  actorUnit,
  targetUnit,
  focusPlayerBy,
}: {
  encounter: KillInfo
  actorUnit?: PlayerUnit
  targetUnit?: PlayerUnit
  focusPlayerBy?: ({ name, id }: { name?: string; id?: string }) => void
}) {
  const isKill = encounter.action === 'KILL'

  return (
    <li
      className={`grid grid-cols-[2.25rem_minmax(0,1fr)] items-start gap-x-2 border-l-2 px-2 py-1.5 text-xs leading-5 @sm/timeline:gap-x-3 @md/timeline:grid-cols-[2.25rem_minmax(0,1fr)_minmax(0,max-content)] @lg/timeline:grid-cols-[2.5rem_minmax(0,1fr)_minmax(0,max-content)] ${
        isKill ? 'border-emerald-600 bg-emerald-500/[0.06]' : 'border-red-600 bg-red-500/[0.06]'
      }`}
      aria-label={isKill ? 'Kill' : 'Death'}
    >
      <time
        className="col-start-1 row-start-1 text-[11px] tabular-nums text-muted-foreground"
        dateTime={`PT${encounter.timestamp}S`}
      >
        {formatTime(encounter.timestamp)}
      </time>
      <span className="col-start-2 row-start-1 flex min-w-0 flex-wrap items-center gap-x-1.5">
        <RoleIcon unit={actorUnit} />
        <span className="sr-only">{isKill ? 'killed' : 'was killed by'}</span>
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
          with <span className="font-medium text-foreground">{encounter.weapon}</span>
        </span>
      )}
    </li>
  )
}

type CapturingTeam = 'allies' | 'axis'

type TimelineEntry =
  | { type: 'encounter'; encounter: KillInfo; encounterIndex: number; timestamp: number }
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

function teamName(team: TeamId) {
  return team === 1 ? 'Allies' : 'Axis'
}

function playerStateEvents(units: PlayerUnit[]): PlayerStateEvent[] {
  const events: PlayerStateEvent[] = []
  let lastTeam: TeamId | undefined
  let hasJoined = false
  let isDisconnected = false
  const orderedUnits = [...units].sort((a, b) => a.ts - b.ts)

  orderedUnits.forEach((unit) => {
    const offline = unit.t === -111 && unit.s === -111 && unit.r === -111

    if (offline) {
      if (hasJoined && !isDisconnected) events.push({ kind: 'disconnected', timestamp: unit.ts })
      isDisconnected = true
      return
    }

    // The default rifleman with no squad is a lobby placeholder. Other roles may
    // retain -111 after a deployed player is removed from their squad.
    if (unit.s === -111 && unit.r === 0) return

    if (!isTeamId(unit.t)) return

    if (!hasJoined) {
      events.push({ kind: 'joined', timestamp: unit.ts, team: unit.t })
      hasJoined = true
    } else if (isDisconnected && lastTeam) {
      events.push({ kind: 'reconnected', timestamp: unit.ts, team: unit.t, previousTeam: lastTeam })
    } else if (lastTeam && unit.t !== lastTeam) {
      events.push({ kind: 'switched', timestamp: unit.ts, team: unit.t, previousTeam: lastTeam })
    }

    lastTeam = unit.t
    isDisconnected = false
  })

  return events
}

function PlayerStateMarker({ event, playerName }: { event: PlayerStateEvent; playerName: string }) {
  let description: ReactNode

  if (event.kind === 'joined') {
    description = (
      <>
        joined as <span className="font-medium text-foreground">{teamName(event.team)}</span>
      </>
    )
  } else if (event.kind === 'disconnected') {
    description = 'disconnected'
  } else if (event.kind === 'switched') {
    description = (
      <>
        switched from <span className="font-medium text-foreground">{teamName(event.previousTeam)}</span> to{' '}
        <span className="font-medium text-foreground">{teamName(event.team)}</span>
      </>
    )
  } else if (event.team !== event.previousTeam) {
    description = (
      <>
        reconnected as <span className="font-medium text-foreground">{teamName(event.team)}</span> after switching teams
      </>
    )
  } else {
    description = (
      <>
        reconnected as <span className="font-medium text-foreground">{teamName(event.team)}</span>
      </>
    )
  }

  return (
    <li className="px-2 py-1">
      <Marker variant="separator" className="text-xs">
        <MarkerContent>
          <time className="tabular-nums" dateTime={`PT${event.timestamp}S`}>
            {formatTime(event.timestamp)}
          </time>{' '}
          <span className="font-semibold text-foreground">{playerName}</span> {description}
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
  const encounters = 'encounters' in player && player.encounters ? player.encounters : []
  const units = 'units' in player && player.units ? player.units : []
  const stateEvents = playerStateEvents(units)
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
  const streakStarts = new Map<number, string>()
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
      timestamp: encounter.timestamp,
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
    if (a.type === 'encounter' && b.type === 'encounter') return a.encounterIndex - b.encounterIndex
    if (a.type === 'cap-flip' && b.type === 'cap-flip') return a.capFlipIndex - b.capFlipIndex
    if (a.type === 'player-state' && b.type === 'player-state') return a.playerStateIndex - b.playerStateIndex
    return 0
  })

  return (
    <ol
      className="@container/timeline flex w-full list-none flex-col overflow-y-auto py-2 pr-1"
      aria-label="Encounters Timeline"
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
          const playerTeam = unitAt(units, entry.timestamp)?.t
          const capturedTeamId = entry.capturedBy === 'allies' ? 1 : entry.capturedBy === 'axis' ? 2 : undefined
          const captureDescription = capturedTeamId
            ? playerTeam === capturedTeamId
              ? `${player.player}'s team captured an objective`
              : isTeamId(playerTeam)
                ? `${player.player}'s team lost an objective`
                : `${teamName(capturedTeamId)} captured an objective`
            : 'Score'

          return (
            <li key={`cap-flip-${entry.timestamp}-${entry.capFlipIndex}`} className="px-2 py-1">
              <Marker variant="separator" className="text-xs">
                <MarkerContent>
                  <time className="tabular-nums" dateTime={`PT${entry.timestamp}S`}>
                    {formatTime(entry.timestamp)}
                  </time>{' '}
                  {captureDescription} ·{' '}
                  <span className="font-medium text-foreground">
                    Allies {entry.flip.allied_score} — {entry.flip.axis_score} Axis
                  </span>
                </MarkerContent>
              </Marker>
            </li>
          )
        }

        const { encounter, encounterIndex } = entry
        const actorUnit = unitAt(units, encounter.timestamp)
        const targetUnits = players.find(({ id }) => id === encounter.player_id)?.units ?? []
        const title = streakStarts.get(encounterIndex)
        const endedCount = streakEnds.get(encounterIndex)

        return (
          <Fragment
            key={`encounter-${encounter.timestamp}-${encounter.action}-${encounter.player_id}-${encounterIndex}`}
          >
            {title && (
              <li className="px-2 py-1">
                <Marker variant="separator" className="text-xs text-amber-700 dark:text-amber-400">
                  <MarkerContent>
                    <span className="font-semibold">{player.player}:</span> {title}
                  </MarkerContent>
                </Marker>
              </li>
            )}
            {endedCount && (
              <li className="px-2 py-1">
                <Marker variant="separator" className="text-xs text-amber-700 dark:text-amber-400">
                  <MarkerContent>
                    <span className="font-semibold">{player.player}:</span> streak ended at {endedCount} kills
                  </MarkerContent>
                </Marker>
              </li>
            )}
            <EncounterItem
              encounter={encounter}
              actorUnit={actorUnit}
              targetUnit={unitAt(targetUnits, encounter.timestamp)}
              focusPlayerBy={focusPlayerBy}
            />
          </Fragment>
        )
      })}
    </ol>
  )
}
