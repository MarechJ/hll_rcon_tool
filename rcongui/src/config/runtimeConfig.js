const supportedGames = new Set(["hll", "hllv"]);
const configuredGame = window.__CRCON_CONFIG__?.HLL_GAME ?? "hll";

if (!supportedGames.has(configuredGame)) {
  throw new Error(`Unsupported runtime HLL_GAME '${configuredGame}'`);
}

export const runtimeConfig = Object.freeze({
  HLL_GAME: configuredGame,
});
