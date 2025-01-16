import React, {cloneElement, ReactElement} from 'react'
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from "@/components/ui/tooltip";
import {MapEnvironment} from "@/types/mapLayer";
import {CloudFog, CloudRain, Moon, Sun, Sunrise, Sunset} from "lucide-react";
import {useTranslation} from "react-i18next";

type WeatherIconProps = {
  environment: MapEnvironment
} & React.HTMLAttributes<HTMLDivElement>

const weatherToIcon: Record<MapEnvironment, ReactElement> = {
  ["day"]: <Sun/>,
  ["night"]: <Moon/>,
  ["dusk"]: <Sunrise/>,
  ["dawn"]: <Sunset/>,
  ["rain"]: <CloudRain/>,
  ["overcast"]: <CloudFog/>,
};

export default function WeatherIcon({ environment, className, ...props }: WeatherIconProps) {
  const { t } = useTranslation('game');
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div {...props}>
            {cloneElement(weatherToIcon[environment], {
              className: className
            })}
          </div>
        </TooltipTrigger>
        <TooltipContent>
          {t(`weather.${environment}`)}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
