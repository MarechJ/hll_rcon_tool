const supportedGames = new Set(["hll", "hllv"]);

const configuredGame = import.meta.env.DEV
  ? import.meta.env.VITE_HLL_GAME ?? "hll"
  : window.__CRCON_CONFIG__?.HLL_GAME ?? "hll";

if (!supportedGames.has(configuredGame)) {
  throw new Error(`Unsupported HLL_GAME '${configuredGame}'`);
}

export const runtimeConfig = Object.freeze({
  HLL_GAME: configuredGame,
});