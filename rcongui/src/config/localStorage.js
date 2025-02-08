export default {
  LIVE_PLAYERS_TABLE_CONFIG: {
    key: "live-players-table-config",
    defaultValue: {
      density: "dense",
      fontSize: "small",
      expandedView: false,
      columnVisibility: {
        player_id: false,
      },
    },
  },
  PLAYERS_TABLE_CONFIG: {
    key: "players-table-config",
    defaultValue: {
      density: "normal",
      fontSize: "normal",
    },
  },
  LIVE_LOGS_TABLE_CONFIG: {
    key: "live-logs-table-config",
    defaultValue: {
      density: "normal",
      fontSize: "normal",
      highlighted: false,
      actions: [],
      filters: {
        actions: {
          selected: [],
          enabled: true,
        },
      },
      columnVisibility: {},
    },
  },
  LIVE_LOGS_SEARCH_PARAMS: {
    key: "live-logs-search-params",
    defaultValue: {
      players: [],
      actions: [],
      inclusive_filter: true,
      limit: 500,
    },
  },
  GAMES_TABLE_CONFIG: {
    key: "games-table-config",
    defaultValue: {
      density: "normal",
      fontSize: "normal",
    },
  },
};
