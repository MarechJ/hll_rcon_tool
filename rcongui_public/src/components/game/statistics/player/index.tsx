import { Player, PlayerWithStatus } from '@/types/player'
import { isPlayerWithStatus } from '@/components/game/statistics/player/utils'
import { Status } from '@/components/game/statistics/player-status'
import { points, scores, isSteamPlayer, getSteamProfileUrl, getXboxProfileUrl } from './utils'
import { Button } from '@/components/ui/button'
import { SimpleIcon } from '@/components/simple-icon'
import { siSteam } from 'simple-icons'
import { Gamepad2Icon} from 'lucide-react'
import { SimpleTable } from '@/components/game/statistics/simple-table'
import { ScrollArea } from '@/components/ui/scroll-area'
import { IconStatistic } from '../icon'
import { columns as faceoffColumns } from '../faceoff-columns'
import { deathByColumns, killByColumns } from '../weapons-columns'
import { mergeKillsDeaths } from '../utils'
import { useTranslation } from 'react-i18next'
import {Accordion, AccordionContent, AccordionItem, AccordionTrigger} from "@/components/ui/accordion";
import {AccordionHeader} from "@radix-ui/react-accordion";
import {useGameStatsContext} from "@/components/game/statistics/game-stats-container";

export default function PlayerGameDetail({
  player,
  isMobile,
}: {
  player: Player | PlayerWithStatus
  isMobile?: boolean
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

  const { focusPlayerByName } = useGameStatsContext();

  return (
    <div className="divide-y pb-2 lg:sticky lg:top-14 border">
      {!isMobile && (
        <div className="flex justify-between items-center gap-1 px-2 h-12">
          <div className="flex justify-center items-center gap-2 grow">
            {isPlayerWithStatus(player) && player.is_online ? (
              <Status player={player} className="animate-ping" />
            ) : isPlayerWithStatus(player) ? (
              <Status player={player} />
            ) : null}
            <Button
              variant="text"
              className="pl-0 h-0 text-xl"
              onClick={() => focusPlayerByName(player.player)}
            >
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
          <Accordion type="single" collapsible>
            <AccordionItem value="encounters">
              <AccordionHeader>
                <AccordionTrigger>
                  {t('playerStats.encounters')}
                </AccordionTrigger>
              </AccordionHeader>
              <AccordionContent>
                <SimpleTable columns={faceoffColumns} data={mergeKillsDeaths(player)} initialSortedColumn="kills"/>
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="killsByWeapon">
              <AccordionHeader>
                <AccordionTrigger>
                  {t('playerStats.killsByWeapon')}
                </AccordionTrigger>
              </AccordionHeader>
              <AccordionContent>
                <SimpleTable columns={killByColumns} data={killsBy} initialSortedColumn="count"/>
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="deathsByWeapon">
              <AccordionHeader>
                <AccordionTrigger>
                  {t('playerStats.deathsByWeapon')}
                </AccordionTrigger>
              </AccordionHeader>
              <AccordionContent>
                <SimpleTable columns={deathByColumns} data={deathsBy} initialSortedColumn="count"/>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </ScrollArea>
    </div>
  )
}
