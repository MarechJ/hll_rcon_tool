import colors from 'tailwindcss/colors'
import { SimpleWeaponType } from '@/types/weapon'

export const SIMPLE_WEAPON_TYPE_COLORS: Record<SimpleWeaponType, string> = {
  [SimpleWeaponType.Sniper]: colors.emerald[500],
  [SimpleWeaponType.Infantry]: colors.lime[500],
  [SimpleWeaponType.MachineGun]: colors.red[600],
  [SimpleWeaponType.Explosive]: colors.amber[600],
  [SimpleWeaponType.Armor]: colors.cyan[400],
  [SimpleWeaponType.Artillery]: colors.fuchsia[600],
  [SimpleWeaponType.SPA]: colors.fuchsia[400],
  [SimpleWeaponType.Commander]: colors.amber[300],
}
