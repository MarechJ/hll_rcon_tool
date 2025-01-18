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

  const GAP_SIZE = 2.5;

  const {t} = useTranslation("game");

  if (!totalKills || !killsByType) {
    return null;
  }

  /**
   *  Sorted by a specific order. Please consider this before sorting it by value:
   *  It is sorted from direct to indirect weapon categories
   *  Sniper is super accurate, infantry less accurate, mg is more spray and then explosions sorted by splash size
   */
  const simpleWeaponTypeMap: Record<SimpleWeaponType, {color: string, order: number, t: string}> = {
    [SimpleWeaponType.Sniper]: { color: colors.emerald[500], order: 0, t: t("weaponType.sniper") },
    [SimpleWeaponType.Infantry]: { color: colors.lime[500], order: 1, t: t("weaponType.infantry") },
    [SimpleWeaponType.MachineGun]: { color: colors.red[600], order: 2, t: t("weaponType.machineGun") },
    [SimpleWeaponType.Explosive]: { color: colors.amber[600], order: 3, t: t("weaponType.explosive") },
    [SimpleWeaponType.Armor]: { color: colors.cyan[400], order: 4, t: t("weaponType.armor") },
    [SimpleWeaponType.Artillery]: { color: colors.fuchsia[600], order: 5, t: t("weaponType.artillery") },
    [SimpleWeaponType.Commander]: { color: colors.amber[300], order: 6, t: t("weaponType.commander") },
  };

  const killsBySimpleStatus = new Map<SimpleWeaponType, number>;
  let totalCategorizedKills = 0;

  Object.entries(killsByType).forEach(([type, count]) => {
    const simpleType = weaponTypeToSimpleWeaponType[type as WeaponType];
    killsBySimpleStatus.set(simpleType as SimpleWeaponType, (killsBySimpleStatus.get(simpleType) ?? 0) + count);
    totalCategorizedKills += count;
  });

  const displayedBars = Array.from(killsBySimpleStatus.entries())
    .filter(([_, value]) => value > 0)
    /**
    *  Sorted by a specific order. Please read comment at {@link simpleWeaponTypeMap}
    */
    .sort(([a, n1], [b, n2]) =>
      simpleWeaponTypeMap[a].order - simpleWeaponTypeMap[b].order
    );

  const gapAmount = displayedBars.length - 1 + (totalCategorizedKills < totalKills ? 1 : 0);

  return <TooltipProvider>
    <Tooltip>
      <TooltipTrigger asChild>
        <div className={"h-full w-full flex items-center pr-4"}>
          <div className="h-1 w-full flex rounded-full overflow-hidden">
            {displayedBars.map(([type, value], index) => {
              return <React.Fragment key={index}>
                <div
                  style={{
                    width: `calc(${value / totalKills} * (100% - ${gapAmount * GAP_SIZE}px))`,
                    background: simpleWeaponTypeMap[type as SimpleWeaponType].color
                  }}
                />
                {index < gapAmount && <div style={{width: GAP_SIZE + 'px'}}/>}
              </React.Fragment>
              }
            )}
            <div className="bg-gray-500 flex-grow"/>
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
