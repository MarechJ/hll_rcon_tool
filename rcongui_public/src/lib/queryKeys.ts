export const queryKeys = {
  publicInfo: ['public-info'],
  liveStats: ['live-stats'],
  liveSessions: ['live-sessions'],
  games: (page: number, pageSize: number) => ['games', page, pageSize],
  gameDetail: (gameId: number) => ['game', gameId],
}
