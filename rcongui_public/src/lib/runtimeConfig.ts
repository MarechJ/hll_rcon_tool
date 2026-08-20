export type HllGame = 'hll' | 'hllv'

declare global {
  interface Window {
    __CRCON_CONFIG__?: {
      HLL_GAME?: string
    }
  }
}

const configuredGame = window.__CRCON_CONFIG__?.HLL_GAME ?? 'hll'

if (configuredGame !== 'hll' && configuredGame !== 'hllv') {
  throw new Error(`Unsupported runtime HLL_GAME '${configuredGame}'`)
}

export const runtimeConfig = Object.freeze({
  HLL_GAME: configuredGame as HllGame,
})
