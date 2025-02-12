import {Slider} from "@/components/ui/slider";
import React from "react";
import StreamBanner, {StreamSettings} from "@/pages/home/streaming/stream-banner";
import {Input} from "@/components/ui/input";
import {Switch} from "@/components/ui/switch";
import {useTranslation} from "react-i18next";
import {useOutletContext} from "react-router";
import {GameLiveOutletContext} from "@/pages/home/layout";
import SelectBox from "@/components/ui/select-box";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger
} from "@/components/ui/accordion";
import {AccordionHeader} from "@radix-ui/react-accordion";
import {GraduationCap} from "lucide-react";
import StreamTutorial from "@/pages/home/streaming/stream-tutorial";
import {useStorageState} from "@/hooks/use-storage-state";

export default function Streaming() {
  const { t } = useTranslation('translation', {keyPrefix: 'streaming'});

  const { liveStats } = useOutletContext<GameLiveOutletContext>();

  const [streamSettings, setStreamSettings] = useStorageState<StreamSettings>('stream-settings', {
    playerFilter: [],
    playerAmount: 5,
    animationDuration: 15,
    pauseWidth: 150,
    text: 'TOP KILLS:',
    showAvatars: false,
    showWeapons: false,
  })

  const playerFilterOptions = liveStats.data
    .map((player) => ({ value: player.player, label: player.player }))
    .concat(
      streamSettings.playerFilter
        .filter((name) => !liveStats.data.some((player) => player.player === name))
        .map((name) => ({ value: name, label: name })),
    );

  return <div className="w-full lg:w-2/3">
    <h1 className="text-2xl text-center pb-6">{t("streamerView")}</h1>
    <Accordion type="single" collapsible className="border-x border-t bg-background">
      <AccordionItem value="tutorial">
        <AccordionHeader>
          <AccordionTrigger>
            <span className="w-full flex flex-row items-center justify-center"><GraduationCap className="inline-block size-7 mr-1"/> {t('tutorial.title')}</span>
          </AccordionTrigger>
        </AccordionHeader>
        <AccordionContent>
          <StreamTutorial/>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
    {/*bg background necessary so the background stays within obs*/}
    <div className="bg-background w-full border-x border-b gap-3 p-2 flex flex-wrap">
      <div className="w-52 h-12 flex flex-col justify-between pb-2">
        <span className="text-nowrap">
          {t('playerCount')} ({streamSettings.playerAmount})
        </span>
        <Slider onValueChange={value => setStreamSettings(prev => ({...prev, playerAmount: value[0]}))}
                value={[streamSettings.playerAmount]}
                max={25} step={1}/>
      </div>
      <div className="w-52 h-12 flex flex-col justify-between pb-2">
        <span className="text-nowrap">
          {t('cycleDuration')} ({streamSettings.animationDuration}s)
        </span>
        <Slider onValueChange={value => setStreamSettings(prev => ({...prev, animationDuration: value[0]}))}
                value={[streamSettings.animationDuration]}
                max={60} step={1}/>
      </div>
      <div className="w-52 h-12 flex flex-col justify-between pb-2">
        <span className="text-nowrap">
          {t('pauseWidth')} ({streamSettings.pauseWidth})
        </span>
        <Slider onValueChange={value => setStreamSettings(prev => ({...prev, pauseWidth: value[0]}))}
                value={[streamSettings.pauseWidth]}
                max={1000} step={10}/>
      </div>
      <div className="w-52 text-nowrap flex-1">
        <Input placeholder={t('text')} value={streamSettings.text} onChange={(e) => setStreamSettings(prev => ({...prev, text: e.target.value}))}/>
      </div>
      <div className="w-52 h-10 text-nowrap items-center flex">
        <span className="pr-4">
          {t('showAvatars')}:
        </span>
        <Switch checked={streamSettings.showAvatars} onCheckedChange={(value) => setStreamSettings(prev => ({...prev, showAvatars: value}))}/>
      </div>
      <div className="w-52 h-10 text-nowrap items-center flex">
        <span className="pr-4">
          {t('showWeapons')}:
        </span>
        <Switch checked={streamSettings.showWeapons} onCheckedChange={(value) => setStreamSettings(prev => ({...prev, showWeapons: value}))}/>
      </div>
      <div className="flex-1">
        <SelectBox
          options={playerFilterOptions}
          multiple
          value={streamSettings.playerFilter}
          onChange={(values) => Array.isArray(values) && setStreamSettings(prev => ({...prev, playerFilter: values}))}
          placeholder={`${t('hidePlayer')}...`}
        />
      </div>
    </div>
    <div className="w-full border-x border-b gap-3 p-2">
      <StreamBanner settings={streamSettings}/>
    </div>
  </div>
}
