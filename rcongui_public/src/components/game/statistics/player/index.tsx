import { Player } from '@/types/player'
import { isPlayerWithStatus } from '@/components/game/statistics/player/utils'
import { Status } from '@/components/game/statistics/player-status'
import { points, scores, isSteamPlayer, getSteamProfileUrl, getXboxProfileUrl } from './utils'
import { Button } from '@/components/ui/button'
import { SimpleIcon } from '@/components/simple-icon'
import { siSteam } from 'simple-icons'
import { Gamepad2Icon } from 'lucide-react'
import { SimpleTable } from '@/components/game/statistics/simple-table'
import { ScrollArea } from '@/components/ui/scroll-area'
import { IconStatistic } from '../icon'
import { columns as faceoffColumns } from '../faceoff-columns'
import { deathByColumns, killByColumns } from '../weapons-columns'
import { mergeKillsDeaths } from '../utils'
import { useTranslation } from 'react-i18next'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { useGameStatsContext } from '@/components/game/statistics/game-stats-container'
import { GamePlayer } from '@/components/game/statistics/game-stats-container'
import { MatchScore } from '@/types/api'
import { Encounters } from '../encounters'
import { RoleTimeline } from '../role-timeline'

export default function PlayerGameDetail({
  player,
  isMobile,
  focusPlayerBy: focusPlayerByProp,
  players,
  capFlips,
}: {
  player: Player
  isMobile?: boolean
  focusPlayerBy?: ({ name, id }: { name?: string; id?: string }) => void
  players?: GamePlayer[]
  capFlips?: MatchScore[]
}) {
  const { t } = useTranslation('game')
  const killsBy = player
    ? Object.entries(player.weapons).map((entry) => ({
        name: entry[0],
        count: entry[1],
      }))
    : []
  killsBy.sort((a, b) => b.count - a.count)

  const deathsBy = player
    ? Object.entries(player.death_by_weapons || {}).map((entry) => ({
        name: entry[0],
        count: entry[1],
      }))
    : []
  deathsBy.sort((a, b) => b.count - a.count)

  const { focusPlayerBy, players: contextPlayers, capFlips: contextCapFlips, gameDuration } = useGameStatsContext()
  const timelinePlayers = players ?? contextPlayers
  const timelineCapFlips = capFlips ?? contextCapFlips

  return (
    <div className="divide-y pb-2 lg:sticky lg:top-14 border">
      {!isMobile && (
        <div className="flex justify-between items-center gap-1 px-2 h-12">
          <div className="flex justify-center items-center gap-2 grow">
            {isPlayerWithStatus(player) && player.status == 'online' ? (
              <Status player={player} className="animate-ping" />
            ) : isPlayerWithStatus(player) ? (
              <Status player={player} />
            ) : null}
            <Button variant="text" className="pl-0 h-0 text-xl" onClick={() => focusPlayerBy({ id: player.player_id })}>
              {player.player}
            </Button>
          </div>
          <div className="flex flex-row justify-center items-center">
            <Button size={'icon'} variant={'outline'} asChild>
              {isSteamPlayer(player) ? (
                <a href={getSteamProfileUrl(player.player_id)} target="_blank" rel="noreferrer">
                  <SimpleIcon icon={siSteam} size={20} className="dark:fill-current" />
                </a>
              ) : (
                <a href={getXboxProfileUrl(player.player)} target="_blank" rel="noreferrer">
                  <Gamepad2Icon />
                </a>
              )}
            </Button>
          </div>
        </div>
      )}
      <ScrollArea className="h-player-detail">
        <div className="divide-y">
          <section className="flex flex-row divide-x justify-around h-10">
            {points.map((point) => (
              <div key={point.key} className="flex flex-col w-1/6 justify-center items-center">
                <img
                  src={point.icon}
                  width={12}
                  height={12}
                  alt={t(point.transKey)}
                  className="mb-[2px] bg-primary dark:bg-transparent"
                />
                <div className="text-sm">{player[point.key]}</div>
              </div>
            ))}
          </section>
          <section className="flex flex-row justify-around h-20">
            {scores.map((score) => {
              const Icon = score.icon
              return (
                <IconStatistic key={score.key} stat={player[score.key]} text={t(score.transKey)}>
                  <Icon size={16} />
                </IconStatistic>
              )
            })}
          </section>
          {'units' in player && player.units?.length > 0 && (
            <RoleTimeline units={player.units} gameDuration={gameDuration} />
          )}
          <section className="">
            <Accordion type="single" collapsible>
              <AccordionItem value="encounters">
                <AccordionTrigger className="px-2">{t('playerStats.encounters')}</AccordionTrigger>
                <AccordionContent>
                  <SimpleTable columns={faceoffColumns} data={mergeKillsDeaths(player)} initialSortedColumn="kills" />
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="killsByWeapon">
                <AccordionTrigger className="px-2">{t('playerStats.killsByWeapon')}</AccordionTrigger>
                <AccordionContent>
                  <SimpleTable columns={killByColumns} data={killsBy} initialSortedColumn="count" />
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="deathsByWeapon">
                <AccordionTrigger className="px-2">{t('playerStats.deathsByWeapon')}</AccordionTrigger>
                <AccordionContent>
                  <SimpleTable columns={deathByColumns} data={deathsBy} initialSortedColumn="count" />
                </AccordionContent>
              </AccordionItem>
              {'encounters' in player && (
                <AccordionItem value="timeline">
                  <AccordionTrigger className="px-2">{t('playerStats.timeline')}</AccordionTrigger>
                  <AccordionContent>
                    <Encounters
                      player={player}
                      focusPlayerBy={focusPlayerByProp ?? focusPlayerBy}
                      players={timelinePlayers}
                      capFlips={timelineCapFlips}
                    />
                  </AccordionContent>
                </AccordionItem>
              )}
            </Accordion>
          </section>
        </div>
      </ScrollArea>
    </div>
  )
}
