import { GameMode, MapLayer, MapTeam } from '@/types/mapLayer'
import { Arrow, RectangleNeutral } from './shapes'
import { useTranslation } from 'react-i18next'
import { useTheme } from '@/hooks/use-theme-provider'
import { getDarkFactionIconSrc, getLightFactionIconSrc } from '@/constants/factions'
import { FactionEnum } from '@/types/player'
import { MatchScore } from '@/types/api'
import { cn } from '@/lib/utils'
import { HoverCard, HoverCardContent, HoverCardTrigger } from '@/components/ui/hover-card'
import { Flag, Swords } from 'lucide-react'
import plugin from 'dayjs/plugin/duration';

type GameOverviewProps = {
  time: plugin.Duration
  map: MapLayer
  allies: MapTeam
  axis: MapTeam
  mode: GameMode
  mapName: string
  alliesCount?: number
  axisCount?: number
  score: {
    allies: number | undefined
    axis: number | undefined
  }
  capFlips?: MatchScore[]
  matchTime?: number
  remainingTime?: number
}

type Score = {
  allies: number | undefined
  axis: number | undefined
}

const ArrowsContainer = ({ children }: { children: React.ReactNode }) => {
  return <div className="w-full h-4 md:h-6 lg:h-8 flex flex-row px-2 mb-1">{children}</div>
}

const MAX_SCORE = 5

const OffensiveArrows = ({ score, map }: { score: Score; map: MapLayer }) => (
  <>
    {Array(score.allies)
      .fill(null)
      .map((_, index) => (
        <Arrow
          key={`score-${index}`}
          direction={map.attackers === 'allies' ? 'right' : 'left'}
          team="allies"
          mode="offensive"
          order={index}
          highlighted={index === 4}
        />
      ))}
    {Array(score.axis)
      .fill(null)
      .map((_, index) => (
        <Arrow
          key={`score-${index}`}
          direction={map.attackers === 'allies' ? 'right' : 'left'}
          team="axis"
          mode="offensive"
          highlighted={index === 0}
          order={(score.allies ?? 0) + index}
        />
      ))}
  </>
)

const WarfareArrows = ({ score }: { score: Score }) => {
  const isGameFinished = score.allies === MAX_SCORE || score.axis === MAX_SCORE
  const isTied = score.allies === score.axis
  const shouldHighlight = !isTied && !isGameFinished

  return (
    <>
      {Array(score.allies)
        .fill(null)
        .map((_, index, arr) => (
          <Arrow
            key={`score-${index}`}
            direction="right"
            team="allies"
            mode="warfare"
            highlighted={index === arr.length - 1 && shouldHighlight}
          />
        ))}
      {isTied && <RectangleNeutral />}
      {Array(score.axis)
        .fill(null)
        .map((_, index) => (
          <Arrow
            key={`score-${index}`}
            direction="left"
            team="axis"
            mode="warfare"
            highlighted={index === 0 && shouldHighlight}
          />
        ))}
    </>
  )
}

function CapFlipRecord({
  cap,
  faction = null,
  offset = 0,
  timestamp,
  team = null,
}: {
  cap: MatchScore
  faction: FactionEnum | null
  offset: number
  timestamp: string
  team: 'axis' | 'allies' | null
}) {
  if (team === null || faction === null) return null
  return (
    <HoverCard openDelay={50} closeDelay={50}>
      <HoverCardTrigger asChild>
        <button
          className={
            'absolute w-4 h-10 bg-background bottom-0 rounded-sm bg-clip-border border-px transition-all hover:z-10 [clip-path:polygon(20%_0%,80%_0%,100%_20%,100%_80%,80%_100%,20%_100%,0%_80%,0%_20%)]'
          }
          style={{ left: `calc(${offset}% - 8px)` }} // 8 is half the size of the rectangle
        >
          <div className="relative w-full h-full flex justify-between flex-col items-center">
            <div className={cn('h-0.5 w-full', team === 'axis' && 'bg-red-500', team === 'allies' && 'bg-blue-500')}></div>
            <div className="h-4 w-full text-xs font-bold text-center">{cap.allied_score}</div>
            <div className="h-4 w-full text-xs font-bold text-center">{cap.axis_score}</div>
            <div className={cn('h-0.5 w-full', team === 'axis' && 'bg-red-500', team === 'allies' && 'bg-blue-500')}></div>
          </div>
        </button>
      </HoverCardTrigger>
      <HoverCardContent side='bottom' align='center' className={cn(team === 'axis' && 'border-b-red-500', team === 'allies' && 'border-b-blue-500', 'w-16 border-b-4 border-double p-2 text-xs font-bold text-center bg-secondary [clip-path:polygon(50%_0,100%_20%,100%_100%,0_100%,0_20%)]')}>
          <span>{timestamp}</span>
      </HoverCardContent>
    </HoverCard>
  )
}

export function CapFlipsTimeline({ capFlips, matchTime, map, remainingTime }: { capFlips: MatchScore[]; matchTime: number; map: MapLayer, remainingTime: number }) {
  const remainingTimePerc = matchTime ? (remainingTime/matchTime) * 100 : 0
  const capFlipsRecords = capFlips.map((cap, i, arr) => {
    const hours = Math.floor(cap.ts / 3600)
    const mins = Math.floor((cap.ts - hours * 3600) / 60)
    const secs = cap.ts % 60
    const timestamp = `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    let factionKey: keyof typeof FactionEnum | null = null
    let team: 'axis' | 'allies' | null = null
    // which team gained this cap
    if (i > 0) {
      if (arr[i - 1].allied_score < arr[i].allied_score) {
        factionKey = map.map['allies'].name.toUpperCase() as keyof typeof FactionEnum
        team = 'allies'
      } else if (arr[i - 1].axis_score < arr[i].axis_score) {
        factionKey = map.map['axis'].name.toUpperCase() as keyof typeof FactionEnum
        team = 'axis'
      }
    }
    // TODO: this won't work with Offensive
    const faction = factionKey && FactionEnum[factionKey]
    let ts = cap.ts
    if (map.game_mode === "offensive" && i > 0) {
      const timePerCap = matchTime / 5
      ts = (i - 1) * timePerCap + cap.ts - arr[i - 1].ts
    }
    const offset = Math.ceil((ts / matchTime) * 100)
    return { cap, timestamp, faction, team, offset }
  })

  return (
    <div className='px-6 lg:px-8 my-4'>
      <div className="w-full h-10 relative">
        {map.game_mode === "offensive" ? Array(4).fill(null).map((_, i) => (
            <div key={i} className="absolute w-0.5 h-6 bg-secondary left-0 bottom-2" style={{ left: `calc(${20 * (i + 1) }% - 1px)`}}></div>
        )) : null}
        <Swords size={20} className='absolute top-2 -left-6' />
        <div className='relative w-full h-full overflow-hidden'>
          <div className="absolute w-full border-t-4 border-2 border-secondary left-0 bottom-4.5"></div>
          <div className="absolute w-full h-0.5 bg-primary bottom-5 -translate-x-full transition-all duration-[15s]" style={{ translate: `-${remainingTimePerc}%` }}></div>
        </div>
        <ol className="absolute w-full bottom-0 left-0">
          {capFlipsRecords.map((flip) => (
            <li key={flip.timestamp}>
              <CapFlipRecord {...flip} />
            </li>
          ))}
        </ol>
        <Flag size={20} className='absolute top-2 -right-6' />
      </div>
    </div>
  )
}

export default function GameOverview({
  map,
  time,
  allies,
  axis,
  mode,
  mapName,
  axisCount,
  alliesCount,
  score,
  capFlips,
  matchTime,
  remainingTime,
}: GameOverviewProps) {
  const { t } = useTranslation('game')
  const theme = useTheme()

  const getFactionIconSrc = theme.theme === "dark" ? getLightFactionIconSrc : getDarkFactionIconSrc

  const displayArrows = () => {
    if (score.allies === undefined || score.axis === undefined) return null

    return (
      <ArrowsContainer>
        {mode === 'offensive' && <OffensiveArrows score={score} map={map} />}
        {mode === 'warfare' && <WarfareArrows score={score} />}
      </ArrowsContainer>
    )
  }

  return (
    <div className="flex flex-col w-full pt-1">
      {displayArrows()}
      <div className="text-sm text-center">{time.format('H:mm:ss')}</div>
      <div className="flex flex-row justify-center items-center lg:px-2">
        <div className="flex flex-row justify-between basis-full">
          <div className="flex justify-start size-12 lg:size-16">
            <img src={getFactionIconSrc(allies.name)} alt={allies.team} width={64} height={64} />
          </div>
          <div className="flex flex-col text-right flex-grow">
            <div className="text-lg lg:text-2xl font-bold uppercase">{t(allies.team)}</div>
            <div className="flex flex-row text-sm">
              <div className="hidden sm:block flex-grow self-center border-b-[6px] mx-1 border-blue-500 border-double"></div>
              {alliesCount !== undefined && (
                <div className="flex-grow sm:flex-grow-0">
                  {alliesCount} {alliesCount === 1 ? t('player') : t('players')}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="text-4xl lg:text-6xl basis-1/2 min-w-24 lg:min-w-40 text-center">
          {score.allies ?? '?'} : {score.axis ?? '?'}
        </div>

        <div className="flex flex-row justify-between basis-full">
          <div className="flex flex-col text-left w-full">
            <div className="text-lg lg:text-2xl font-bold uppercase">{t(axis.team)}</div>
            <div className="flex flex-row text-sm">
              {axisCount !== undefined && (
                <div>
                  {axisCount} {axisCount === 1 ? t('player') : t('players')}
                </div>
              )}
              <div className="hidden sm:block flex-grow self-center border-b-[6px] mx-1 border-red-500 border-double"></div>
            </div>
          </div>
          <div className="flex justify-start size-12 lg:size-16">
            <img src={getFactionIconSrc(axis.name)} alt={axis.team} width={64} height={64} style={{ maxWidth: 'none' }} />
          </div>
        </div>
      </div>
      <div className="flex flex-col text-center justify-between">
        <div className="flex flex-row">
          <div className="sm:hidden w-full self-center border-t-[6px] mx-1 border-blue-500 border-double"></div>
          <div className="sm:w-full min-w-fit text-sm">{mapName}</div>
          <div className="sm:hidden w-full self-center border-t-[6px] mx-1 border-red-500 border-double"></div>
        </div>
        <div className="text-xs capitalize">
          {mode}
          {map.attackers && ` - ${map.attackers}`}
        </div>
      </div>
      {capFlips && <CapFlipsTimeline capFlips={capFlips} matchTime={matchTime ?? 0} map={map} remainingTime={remainingTime ?? 0} />}
    </div>
  )
}
