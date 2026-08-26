import { keepPreviousData, queryOptions } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";

export const DEFAULT_RECORD_FILTERS = {
  player_id: "",
  reason: "",
  blacklist_id: "",
  exclude_expired: false,
  page_size: 50,
  page: 1,
};

export function getBlacklistRecordFilters(searchParams) {
  const value = (name) => searchParams.get(name) ?? "";

  return {
    player_id: value("player_id"),
    reason: value("reason"),
    blacklist_id: value("blacklist_id"),
    exclude_expired: value("exclude_expired") === "true",
    page_size: Number(value("page_size")) || DEFAULT_RECORD_FILTERS.page_size,
    page: Number(value("page")) || DEFAULT_RECORD_FILTERS.page,
  };
}

function compactParams(filters) {
  return Object.fromEntries(
    Object.entries(filters).filter(
      ([, value]) => value !== "" && value !== null && value !== undefined
    )
  );
}

export const blacklistQueryKeys = {
  all: [{ queryIdentifier: "blacklists" }],
  lists: [{ queryIdentifier: "get_blacklists" }],
  records: (filters) => [
    { queryIdentifier: "get_blacklist_records", ...filters },
  ],
  servers: [{ queryIdentifier: "blacklist_servers" }],
};

export const blacklistQueryOptions = {
  lists: () =>
    queryOptions({
      queryKey: blacklistQueryKeys.lists,
      queryFn: () => cmd.GET_BLACKLISTS(),
      staleTime: 30_000,
    }),
  records: (filters) =>
    queryOptions({
      queryKey: blacklistQueryKeys.records(filters),
      queryFn: () =>
        cmd.GET_BLACKLIST_RECORDS({ params: compactParams(filters) }),
      placeholderData: keepPreviousData,
    }),
  servers: () =>
    queryOptions({
      queryKey: blacklistQueryKeys.servers,
      queryFn: async () => {
        const [currentServerResult, serverListResult] = await Promise.allSettled([
          cmd.GET_CRCON_SERVER_CONNECTION(),
          cmd.GET_GAME_SERVER_LIST(),
        ]);
        const currentServer = currentServerResult.status === "fulfilled"
          ? currentServerResult.value
          : null;
        const serverList = serverListResult.status === "fulfilled"
          ? serverListResult.value
          : [];
        const servers = Object.fromEntries(
          (serverList ?? []).map((server) => [server.server_number, server.name])
        );
        if (currentServer?.server_number !== undefined) {
          servers[currentServer.server_number] = currentServer.name;
        }
        return servers;
      },
      staleTime: 60_000,
    }),
};

export const blacklistMutationOptions = {
  createList: {
    mutationFn: (data) =>
      cmd.CREATE_BLACKLIST({
        payload: {
          name: data.name,
          servers: data.servers,
          sync: data.syncMethod,
        },
        throwRouteError: false,
      }),
  },
  editList: {
    mutationFn: ({ id, ...data }) =>
      cmd.EDIT_BLACKLIST({
        payload: {
          blacklist_id: id,
          name: data.name,
          servers: data.servers,
          sync_method: data.syncMethod,
        },
        throwRouteError: false,
      }),
  },
  deleteList: {
    mutationFn: (blacklist) =>
      cmd.DELETE_BLACKLIST({
        payload: { blacklist_id: blacklist.id },
        throwRouteError: false,
      }),
  },
  createRecord: {
    mutationFn: (data) => {
      const playerIds = data.playerIds?.length ? data.playerIds : [data.playerId];
      return Promise.all(playerIds.map((playerId) =>
        cmd.ADD_BLACKLIST_RECORD({
          payload: {
            blacklist_id: data.blacklistId,
            player_id: playerId,
            expires_at: data.expiresAt?.toISOString?.() ?? data.expiresAt ?? null,
            reason: data.reason,
          },
          throwRouteError: false,
        })
      ));
    },
  },
  editRecord: {
    mutationFn: ({ id, ...data }) =>
      cmd.EDIT_BLACKLIST_RECORD({
        payload: {
          record_id: id,
          blacklist_id: data.blacklistId,
          player_id: data.playerId,
          expires_at: data.expiresAt?.toISOString?.() ?? data.expiresAt ?? null,
          reason: data.reason,
        },
        throwRouteError: false,
      }),
  },
  expireRecord: {
    mutationFn: (record) =>
      cmd.EDIT_BLACKLIST_RECORD({
        payload: { record_id: record.id, expires_at: new Date().toISOString() },
        throwRouteError: false,
      }),
  },
  deleteRecord: {
    mutationFn: (record) =>
      cmd.DELETE_BLACKLIST_RECORD({
        payload: { record_id: record.id },
        throwRouteError: false,
      }),
  },
};
