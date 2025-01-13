import {Slider} from "@/components/ui/slider";
import React, {useState} from "react";
import StreamBanner from "@/pages/home/streaming/stream-banner";
import {Input} from "@/components/ui/input";
import {Switch} from "@/components/ui/switch";
import {useTranslation} from "react-i18next";
import {useOutletContext} from "react-router";
import {GameLiveOutletContext} from "@/pages/home/layout";
import SelectBox from "@/components/ui/select-box";

export default function Streaming() {
  const { t } = useTranslation('translation', {keyPrefix: 'streaming'});

  const { liveStats } = useOutletContext<GameLiveOutletContext>();

  const [playerFilter, setPlayerFilter] = useState<string[]>([]);

  const [playerAmount, setPlayerAmount] = useState<number>(5);
  const [animationDuration, setAnimationDuration] = useState<number>(15);
  const [pauseWidth, setPauseWidth] = useState<number>(150);
  const [text, setText] = useState<string>('TOP KILLS:');
  const [showAvatars, setShowAvatars] = useState(false);

  const playerFilterOptions = liveStats.data
    .map((player) => ({ value: player.player, label: player.player }))
    .concat(
      playerFilter
        .filter((name) => !liveStats.data.some((player) => player.player === name))
        .map((name) => ({ value: name, label: name })),
    );

  return <div className="w-full lg:w-2/3">
    <div className="w-full border gap-3 p-2 flex flex-wrap">
      <div className="w-52 h-12 flex flex-col justify-between pb-2">
        <span className="text-nowrap">
          {t('playerCount')} ({playerAmount})
        </span>
        <Slider onValueChange={value => setPlayerAmount(value[0])}
                value={[playerAmount]}
                max={25} step={1}/>
      </div>
      <div className="w-52 h-12 flex flex-col justify-between pb-2">
        <span className="text-nowrap">
          {t('cycleDuration')} ({animationDuration}s)
        </span>
        <Slider onValueChange={value => setAnimationDuration(value[0])}
                value={[animationDuration]}
                max={60} step={1}/>
      </div>
      <div className="w-52 h-12 flex flex-col justify-between pb-2">
        <span className="text-nowrap">
          {t('pauseWidth')} ({pauseWidth})
        </span>
        <Slider onValueChange={value => setPauseWidth(value[0])}
                value={[pauseWidth]}
                max={1000} step={10}/>
      </div>
      <div className="w-52 text-nowrap flex-1">
        <Input placeholder={t('text')} value={text} onChange={(e) => setText(e.target.value)}/>
      </div>
      <div className="w-52 h-10 text-nowrap items-center flex">
        <span className="pr-4">
          {t('showAvatars')}:
        </span>
        <Switch checked={showAvatars} onCheckedChange={setShowAvatars}/>
      </div>
      <div className="flex-1">
        <SelectBox
          options={playerFilterOptions}
          multiple
          value={playerFilter}
          onChange={(values) => Array.isArray(values) && setPlayerFilter(values)}
          placeholder={`${t('hidePlayer')}...`}
        />
      </div>
    </div>
    <div className="w-full border-x border-b gap-3 p-2">
      <StreamBanner playerAmount={playerAmount} settings={{animationDuration, text, showAvatars, pauseWidth, playerFilter}}/>
    </div>
  </div>
}
