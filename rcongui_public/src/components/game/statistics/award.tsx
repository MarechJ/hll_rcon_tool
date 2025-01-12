import React, {cloneElement, memo} from 'react'
import {
  BabyIcon,
  BicepsFlexedIcon,
  BombIcon,
  CloudHailIcon,
  CloverIcon,
  CrosshairIcon,
  DrumstickIcon,
  Grape,
  HeartCrackIcon,
  HeartOffIcon,
  HelpCircleIcon,
  InfinityIcon,
  Lightbulb,
  Milk,
  PackageIcon,
  PlaneLandingIcon,
  RocketIcon,
  ScaleIcon,
  Settings,
  SunsetIcon,
  Timer,
  TrophyIcon,
  ZapIcon
} from "lucide-react";
import {useTranslation} from "react-i18next";
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from "@/components/ui/tooltip";
import {cn} from "@/lib/utils";
import {PlayerBaseWithAwards} from "@/pages/games/[id]";

interface AwardsProps {
  player: PlayerBaseWithAwards,
}

export const Awards = memo(({ player }: AwardsProps)=> {
  return <div className="flex row gap-3 justify-end">
    {player.awards.map(value => <Award stat={value.type} amount={value.amount}/>)}
  </div>
});

export const statsMap = {
  'kills': { icon: <TrophyIcon/> },
  'kills_streak': { icon: <ZapIcon/> },
  'deaths': { icon: <InfinityIcon/> },
  'deaths_without_kill_streak': { icon: <Milk/> },
  'teamkills': { icon: <HeartOffIcon/> },
  'deaths_by_tk': { icon: <HeartCrackIcon/> },
  'kill_death_ratio': { icon: <DrumstickIcon/> },
  'kills_by_type.commander': { icon: <PlaneLandingIcon/> },
  'kills_by_type.bazooka': { icon: <RocketIcon/> },
  'kills_by_type.grenade': { icon: <BombIcon/> },
  'kills_by_type.mine': { icon: <SunsetIcon/> },
  'kills_by_type.pak': { icon: <Lightbulb/> },
  'kills_by_type.satchel': { icon: <Timer/> },
  'support': { icon: <PackageIcon/> },
  'zero_deaths': { icon: <CloverIcon/> },
  'zero_kills': { icon: <BabyIcon/> },
  'kd_of_one': { icon: <ScaleIcon/> },
};

type StatKey = keyof typeof statsMap;

interface AwardProps {
  stat: string,
  amount: number,
}

function Award({ stat, amount }: AwardProps) {
  const { t } = useTranslation('game');

  return <TooltipProvider>
    <Tooltip>
      <TooltipTrigger>
        <AwardIcon stat={stat} className={"size-7"}/>
      </TooltipTrigger>
      <TooltipContent>
        <div className="flex flex-row items-center">
          <AwardIcon stat={stat} className="size-8 m-4"/>
          <div className="flex flex-col text-left">
            <span className="text-xl">{t('awards.' + stat + '.title' as unknown as TemplateStringsArray)}</span>
            <span className="">{t('awards.' + stat + '.text' as unknown as TemplateStringsArray, { amount })}</span>
          </div>
        </div>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>;
}

type AwardIconProps = {
  stat: string,
} & React.HTMLAttributes<HTMLDivElement>

function AwardIcon({ stat, className, style, ...props }: AwardIconProps) {
  return <div className={cn("rounded-full bg-foreground text-center items-center", className)} style={{ padding: '2.5px' }} {...props}>
    {cloneElement(statsMap[stat as StatKey]?.icon as React.ReactElement ?? <HelpCircleIcon/>, {
      className: 'text-background size-full'
    })}
  </div>;
}
