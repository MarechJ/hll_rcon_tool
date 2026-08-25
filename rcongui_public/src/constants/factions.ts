export const FACTIONS = {
  CW: 'cw',
  GB: 'gb',
  GER: 'ger',
  RUS: 'rus',
  SOV: 'sov',
  US: 'us',
  CAN: 'can',
} as const

export type Faction = (typeof FACTIONS)[keyof typeof FACTIONS]

const FACTIONS_LABELS: Record<Faction, string> = {
  [FACTIONS.CW]: 'Commonwealth',
  [FACTIONS.GB]: 'Commonwealth',
  [FACTIONS.GER]: 'Germany',
  [FACTIONS.RUS]: 'Soviet Union',
  [FACTIONS.SOV]: 'Soviet Union',
  [FACTIONS.US]: 'United States',
  [FACTIONS.CAN]: 'Canada',
}

export function normalizeFaction(platform?: string | null): Faction | undefined {
  const normalized = platform?.toLowerCase() as Faction | undefined
  return normalized && Object.values(FACTIONS).includes(normalized) ? normalized : undefined
}

export function getPlatformLabel(platform?: string | null): string {
  const normalized = normalizeFaction(platform)
  return normalized ? FACTIONS_LABELS[normalized] : platform || 'Unknown faction'
}

const FACTION_TO_ICON_NAME: Record<Faction, string> = {
  [FACTIONS.CW]: 'gb',
  [FACTIONS.GB]: 'gb',
  [FACTIONS.GER]: 'ger',
  [FACTIONS.RUS]: 'rus',
  [FACTIONS.SOV]: 'rus',
  [FACTIONS.US]: 'us',
  [FACTIONS.CAN]: 'can',
}

export const getLightFactionIconSrc = (faction: Faction) => `/icons/teams/${FACTION_TO_ICON_NAME[faction]}.webp`
export const getDarkFactionIconSrc = (faction: Faction) => `/icons/teams/${FACTION_TO_ICON_NAME[faction]}_dark.webp`

