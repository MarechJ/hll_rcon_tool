import React, {memo} from 'react'
import colors from "tailwindcss/colors";
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from "@/components/ui/tooltip";
import {SimpleWeaponType, WeaponType, weaponTypeToSimpleWeaponType} from "@/types/weapon";
import {useTranslation} from "react-i18next";

type WeaponTypeBarProps = {
  totalKills: number,
  killsByType: Record<WeaponType, number>,
}

export const WeaponTypeBar = memo(({ totalKills, killsByType }: WeaponTypeBarProps) => {

  const {t} = useTranslation("game");

  if (!totalKills || !killsByType) {
    return null;
  }

  const simpleWeaponTypeMap: Record<SimpleWeaponType, {color: string, order: number, t: string}> = {
    [SimpleWeaponType.Infantry]: { color: colors.lime[500], order: 0, t: t("weaponType.infantry") },
    [SimpleWeaponType.Explosive]: { color: colors.amber[600], order: 1, t: t("weaponType.explosive") },
    [SimpleWeaponType.MachineGun]: { color: colors.red[600], order: 2, t: t("weaponType.machineGun") },
    [SimpleWeaponType.Armor]: { color: colors.cyan[400], order: 3, t: t("weaponType.armor") },
    [SimpleWeaponType.Artillery]: { color: colors.fuchsia[600], order: 4, t: t("weaponType.artillery") },
    [SimpleWeaponType.Commander]: { color: colors.amber[300], order: 5, t: t("weaponType.commander") },
  };

  const killsBySimpleStatus = new Map<SimpleWeaponType, number>;
  let totalCategorizedKills = 0;

  Object.entries(killsByType).forEach(([type, count]) => {
    const simpleType = weaponTypeToSimpleWeaponType[type as WeaponType];
    killsBySimpleStatus.set(simpleType as SimpleWeaponType, (killsBySimpleStatus.get(simpleType) ?? 0) + count);
    totalCategorizedKills += count;
  });

  return <TooltipProvider>
    <Tooltip>
      <TooltipTrigger asChild>
        <div className={"h-full w-full flex items-center pr-4"}>
          <div className="h-1 w-full flex rounded-full overflow-hidden bg-gray-500">
            {Array.from(killsBySimpleStatus.entries())
              .sort(([a, n1], [b, n2]) =>
                simpleWeaponTypeMap[a].order - simpleWeaponTypeMap[b].order
              )
              .map(([type, value], index) => {
                return <div
                  key={index}
                  style={{width: `${value / totalKills * 100}%`, background: simpleWeaponTypeMap[type as SimpleWeaponType].color}}
                />
              }
            )}
          </div>
        </div>
      </TooltipTrigger>
      <TooltipContent>
        {Object.entries(simpleWeaponTypeMap).map(([type, props]) =>
          <div className="flex items-center" key={props.t}>
            <span className="w-4 size-2" style={{background: props.color}}/>
            <span className="mx-2">{props.t}</span>
            <span className="ml-auto">{killsBySimpleStatus.has(type as SimpleWeaponType) && ` (${killsBySimpleStatus.get(type as SimpleWeaponType)})`}</span>
          </div>
        )}
        <div className="flex items-center">
          <span className="w-4 size-2 bg-gray-500"/>
          <span className="mx-2">{t("unknown")}</span>
          <span className="ml-auto">{totalCategorizedKills < totalKills && ` (${totalKills - totalCategorizedKills})`}</span>
        </div>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
});
