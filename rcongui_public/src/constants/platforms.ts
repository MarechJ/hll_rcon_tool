export const PLATFORMS = {
  STEAM: 'steam',
  EPIC: 'epic',
  XBOX_LIVE: 'xbl',
  XBOX_SERIES_X: 'xsx',
  PLAYSTATION_NETWORK: 'psn',
  PLAYSTATION_5: 'ps5',
} as const

export type Platform = (typeof PLATFORMS)[keyof typeof PLATFORMS]

const PLATFORM_LABELS: Record<Platform, string> = {
  [PLATFORMS.STEAM]: 'Steam',
  [PLATFORMS.EPIC]: 'Epic Games',
  [PLATFORMS.XBOX_LIVE]: 'Xbox Live',
  [PLATFORMS.XBOX_SERIES_X]: 'Xbox Series X|S',
  [PLATFORMS.PLAYSTATION_NETWORK]: 'PlayStation Network',
  [PLATFORMS.PLAYSTATION_5]: 'PlayStation 5',
}

export function normalizePlatform(platform?: string | null): Platform | undefined {
  const normalized = platform?.toLowerCase() as Platform | undefined
  return normalized && Object.values(PLATFORMS).includes(normalized) ? normalized : undefined
}

export function getPlatformLabel(platform?: string | null): string {
  const normalized = normalizePlatform(platform)
  return normalized ? PLATFORM_LABELS[normalized] : platform || 'Unknown platform'
}

export function getPlatformProfileUrl(
  platform: string | null | undefined,
  playerId: string,
  playerName: string,
): string | undefined {
  switch (normalizePlatform(platform)) {
    case PLATFORMS.STEAM:
      return `https://steamcommunity.com/profiles/${playerId}`
    case PLATFORMS.XBOX_LIVE:
    case PLATFORMS.XBOX_SERIES_X:
      return `https://xboxgamertag.com/search/${encodeURIComponent(playerName)}`
    case PLATFORMS.PLAYSTATION_NETWORK:
    case PLATFORMS.PLAYSTATION_5:
      return `https://psnprofiles.com/${encodeURIComponent(playerName)}`
    default:
      return undefined
  }
}
