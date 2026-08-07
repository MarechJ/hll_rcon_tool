export const HLL_ROLES = [
  'rifleman',
  'assault',
  'automaticrifleman',
  'medic',
  'spotter',
  'support',
  'heavymachinegunner',
  'antitank',
  'engineer',
  'officer',
  'sniper',
  'crewman',
  'tankcommander',
  'armycommander',
  'artilleryobserver',
  'operator',
] as const

export function roleIcon(role: number | undefined, variant: 'default' | 'black' = 'default'): string | undefined {
  const name = role === undefined ? undefined : HLL_ROLES[role]
  return name ? `/icons/roles/${name}${variant === 'black' ? '_black' : ''}.png` : undefined
}

export function roleName(role: number | undefined): string | undefined {
  const name = role === undefined ? undefined : HLL_ROLES[role]
  return name?.replace(/(^|[-_])\w/g, (match) => match.toUpperCase()).replace(/[-_]/g, ' ')
}
