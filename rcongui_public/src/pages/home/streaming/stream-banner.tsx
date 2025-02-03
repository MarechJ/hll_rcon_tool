import { useOutletContext } from 'react-router'
import {GameLiveOutletContext} from "@/pages/home/layout";
import {LivePlayer} from "@/types/player";
import {Avatar, AvatarFallback, AvatarImage} from "@/components/ui/avatar";
import {CircleHelp} from "lucide-react";

interface StreamBannerProps {
  settings: StreamSettings,
}

export interface StreamSettings {
  playerAmount: number,
  animationDuration: number,
  pauseWidth: number,
  text: string,
  showAvatars: boolean,
  showWeapons: boolean,
  playerFilter: string[],
}

export default function StreamBanner({ settings }: StreamBannerProps) {
  const { liveStats } = useOutletContext<GameLiveOutletContext>();

  const displayedPlayers = liveStats.data
    .filter(player => !settings.playerFilter.includes(player.player))
    .sort((a, b) => b.kills - a.kills)
    .slice(0, settings.playerAmount);

  return <div className="stream-banner w-full h-12 inline-flex flex-nowrap bg-white overflow-hidden">
    <Stream players={displayedPlayers} settings={settings}/>
    <Stream players={displayedPlayers} settings={settings}/>
  </div>
}

interface StreamProps {
  players: LivePlayer[],
  settings: StreamSettings,
}

const Stream = ({ players, settings }: StreamProps) => {
  return <div className="flex items-center justify-center animate-infinite-scroll transform" style={{animationDuration: settings.animationDuration + 's'}}>
    <div className="flex-shrink-0" style={{width: settings.pauseWidth}}/>
    <div className="stream-banner-text text-black text-right font-bold text-2xl pb-0.5 whitespace-pre mr-2">
      {settings.text}
    </div>
    {players.map((player =>
      <div className="h-full flex-shrink-0 px-2 py-2 text-black whitespace-nowrap flex items-center mr-3">
        <div className="stream-banner-kills text-primary text-2xl font-bold pb-0.5 mr-2">
          {player.kills}
        </div>
        {settings.showAvatars && player.steaminfo?.profile?.avatar && <Avatar className="size-7 mr-1">
          <AvatarImage
            src={player.steaminfo?.profile?.avatar}
          />
          <AvatarFallback delayMs={600} className="bg-black">
            <CircleHelp className="text-wh  ite"/>
          </AvatarFallback>
        </Avatar>}
        <div className="stream-banner-player block">
          <div>
            {player.player}
          </div>
          {settings.showWeapons && <div className="stream-banner-weapon text-gray-500 text-xs">
            {
              Object.entries(player.weapons)
                .sort(([n1, v1], [n2, v2]) => v2 - v1)[0]?.[0]
                .match(/\[(.*?)\]/)?.[1] || Object.entries(player.weapons)
                .sort(([n1, v1], [n2, v2]) => v2 - v1)[0]?.[0]
            }
          </div>}
        </div>
      </div>
    ))}
  </div>
};

