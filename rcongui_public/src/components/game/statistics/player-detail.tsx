import { Player, PlayerWithStatus } from '@/types/player'
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from '@/components/ui/drawer'
import { Button } from '@/components/ui/button'
import { SimpleIcon } from '@/components/simple-icon'
import { siSteam } from 'simple-icons'
import { Status } from '@/components/game/statistics/player-status'
import { getSteamProfileUrl, getXboxProfileUrl, isPlayerWithStatus, isSteamPlayer } from './player/utils'
import { Gamepad2Icon } from 'lucide-react'
import PlayerGameDetail from './player'
import { useTranslation } from 'react-i18next'
import {useGameStatsContext} from "@/components/game/statistics/game-stats-container";

export function NoPlayerGameDetail() {
  const { t } = useTranslation('game')
  return (
    <div className="w-full px-10 py-5 text-center border lg:sticky lg:top-14">
      <div className="grid items-center border border-dashed w-full h-40 text-2xl">{t('selectPlayer')}</div>
    </div>
  )
}

export function MobilePlayerGameDetail({
  open,
  setOpen,
  player,
}: {
  open: boolean
  setOpen: (open: boolean) => void
  player: Player | PlayerWithStatus
}) {
  const { t } = useTranslation('translation')

  const { focusPlayerByName } = useGameStatsContext();

  return (
    <Drawer open={open} onOpenChange={(open) => setOpen(open)}>
      <DrawerContent className="max-h-[75vh]">
        <div className="mx-auto w-full overflow-y-auto [scrollbar-width:thin]">
          <DrawerHeader>
            <DrawerTitle>
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
            </DrawerTitle>
            <DrawerDescription className="sr-only">Game statistics for {player.player}</DrawerDescription>
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
          </DrawerHeader>
          <div className="p-4 pb-0">
            <PlayerGameDetail player={player} isMobile={true} />
          </div>
          <DrawerFooter>
            <DrawerClose asChild>
              <Button variant="outline" onClick={() => setOpen(false)}>
                {t('close')}
              </Button>
            </DrawerClose>
          </DrawerFooter>
        </div>
      </DrawerContent>
    </Drawer>
  )
}
