import { cmd } from "@/utils/fetchUtils";
import { queryOptions } from "@tanstack/react-query";

// Define query keys to maintain consistent query identifiers
export const vipManagerQueryKeys = {
  vips: [{ queryIdentifier: "get_vip_ids" }],
  vipLists: [{ queryIdentifier: "get_vip_lists" }],
  vipListsForServer: [{ queryIdentifier: "get_vip_lists_for_server" }],
  vipList: [{ queryIdentifier: "get_vip_list" }],
  vipListRecord: [{ queryIdentifier: "get_vip_list_record" }],
  vipStatusForPlayers: [{ queryIdentifier: "get_vip_status_for_player_ids" }],
  activeVipRecords: [{ queryIdentifier: "get_active_vip_records" }],
  inactiveVipRecords: [{ queryIdentifier: "get_inactive_vip_records" }],
  playerVipRecords: [{ queryIdentifier: "get_player_vip_records" }],
  playerVipListRecord: [{ queryIdentifier: "get_player_vip_list_record" }],
  vipListRecords: [{ queryIdentifier: "get_vip_list_records" }],
  allVipRecordsForServer: [{ queryIdentifier: "get_all_vip_records_for_server" }],
};

// Define query options for fetching data
export const vipManagerQueryOptions = {
  // Get all VIPs
  vips: () =>
    queryOptions({
      queryKey: vipManagerQueryKeys.vips,
      queryFn: () => cmd.GET_VIPS(),
    }),

  // Get all VIP lists
  vipLists: (params) =>
    queryOptions({
      queryKey: [...vipManagerQueryKeys.vipLists, params],
      queryFn: () => cmd.GET_VIP_LISTS({ params }),
    }),

  // Get VIP lists for a specific server
  vipListsForServer: () =>
    queryOptions({
      queryKey: vipManagerQueryKeys.vipListsForServer,
      queryFn: () => cmd.GET_VIP_LISTS_FOR_SERVER(),
    }),

  // Get a single VIP list
  vipList: (vipListId, params) =>
    queryOptions({
      queryKey: [...vipManagerQueryKeys.vipList, vipListId, params],
      queryFn: () => cmd.GET_VIP_LIST({ params: { vip_list_id: vipListId, ...params } }),
    }),

  // Get a single VIP list record
  vipListRecord: (recordId) =>
    queryOptions({
      queryKey: [...vipManagerQueryKeys.vipListRecord, recordId],
      queryFn: () => cmd.GET_VIP_LIST_RECORD({ params: { record_id: recordId } }),
    }),

  // Get VIP status for specific players
  vipStatusForPlayers: (playerIds) =>
    queryOptions({
      queryKey: [...vipManagerQueryKeys.vipStatusForPlayers, playerIds],
      queryFn: () => cmd.GET_VIP_STATUS_FOR_PLAYERS({ params: { player_ids: playerIds } }),
    }),

  // Get all active VIP records
  activeVipRecords: (vipListId) =>
    queryOptions({
      queryKey: [...vipManagerQueryKeys.activeVipRecords, vipListId],
      queryFn: () => cmd.GET_ACTIVE_VIP_RECORDS({ params: { vip_list_id: vipListId } }),
    }),

  // Get all inactive VIP records
  inactiveVipRecords: (vipListId) =>
    queryOptions({
      queryKey: [...vipManagerQueryKeys.inactiveVipRecords, vipListId],
      queryFn: () => cmd.GET_INACTIVE_VIP_RECORDS({ params: { vip_list_id: vipListId } }),
    }),

  // Get VIP records for a specific player
  playerVipRecords: (playerId, params) =>
    queryOptions({
      queryKey: [...vipManagerQueryKeys.playerVipRecords, playerId, params],
      queryFn: () => cmd.GET_PLAYER_VIP_RECORDS({ params: { player_id: playerId, ...params } }),
    }),

  // Get a player's VIP list record
  playerVipListRecord: (params) =>
    queryOptions({
      queryKey: [...vipManagerQueryKeys.playerVipListRecord, params],
      queryFn: () => cmd.GET_PLAYER_VIP_LIST_RECORD({ params }),
    }),

  // Get all records for a VIP list
  vipListRecords: (params) =>
    queryOptions({
      queryKey: [...vipManagerQueryKeys.vipListRecords, params],
      queryFn: () => cmd.GET_VIP_LIST_RECORDS({ params }),
    }),

  // Get all VIP records for a server
  allVipRecordsForServer: (serverNumber) =>
    queryOptions({
      queryKey: [...vipManagerQueryKeys.allVipRecordsForServer, serverNumber],
      queryFn: () => cmd.GET_ALL_VIP_RECORDS_FOR_SERVER({ params: { server_number: serverNumber } }),
    }),
};

// Define mutation options for updating data
export const vipManagerMutationOptions = {
  // Delete a VIP
  deleteVip: {
    mutationFn: (playerId) =>
      cmd.DELETE_VIP({
        payload: { player_id: playerId },
        throwRouteError: false,
      }),
  },

  // Add a VIP
  addVip: {
    mutationFn: ({ playerId, description }) =>
      cmd.ADD_VIP({
        payload: { player_id: playerId, description },
        throwRouteError: false,
      }),
  },

  // Create a new VIP list
  createVipList: {
    mutationFn: (vipList) =>
      cmd.CREATE_VIP_LIST({
        payload: vipList,
        throwRouteError: false,
      }),
  },

  // Edit an existing VIP list
  editVipList: {
    mutationFn: (vipList) =>
      cmd.EDIT_VIP_LIST({
        payload: vipList,
        throwRouteError: false,
      }),
  },

  // Delete a VIP list
  deleteVipList: {
    mutationFn: (vipListId) =>
      cmd.DELETE_VIP_LIST({
        payload: { vip_list_id: vipListId },
        throwRouteError: false,
      }),
  },

  // Add a record to a VIP list
  addVipListRecord: {
    mutationFn: (record) =>
      cmd.ADD_VIP_LIST_RECORD({
        payload: record,
        throwRouteError: false,
      }),
  },

  // Edit a VIP list record
  editVipListRecord: {
    mutationFn: (record) =>
      cmd.EDIT_VIP_LIST_RECORD({
        payload: record,
        throwRouteError: false,
      }),
  },

  // Add or edit a VIP list record
  addOrEditVipListRecord: {
    mutationFn: (record) =>
      cmd.ADD_OR_EDIT_VIP_LIST_RECORD({
        payload: record,
        throwRouteError: false,
      }),
  },

  // Bulk add VIP list records
  bulkAddVipListRecords: {
    mutationFn: (records) =>
      cmd.BULK_ADD_VIP_LIST_RECORDS({
        payload: { records },
        throwRouteError: false,
      }),
  },

  // Bulk delete VIP list records
  bulkDeleteVipListRecords: {
    mutationFn: (recordIds) =>
      cmd.BULK_DELETE_VIP_LIST_RECORDS({
        payload: { record_ids: recordIds },
        throwRouteError: false,
      }),
  },

  // Bulk edit VIP list records
  bulkEditVipListRecords: {
    mutationFn: (records) =>
      cmd.BULK_EDIT_VIP_LIST_RECORDS({
        payload: { records },
        throwRouteError: false,
      }),
  },

  // Delete a VIP list record
  deleteVipListRecord: {
    mutationFn: (recordId) =>
      cmd.DELETE_VIP_LIST_RECORD({
        payload: { record_id: recordId },
        throwRouteError: false,
      }),
  },

  // Inactivate expired VIP records
  inactivateExpiredVipRecords: {
    mutationFn: () =>
      cmd.INACTIVATE_EXPIRED_VIP_RECORDS({
        throwRouteError: false,
      }),
  },

  // Extend VIP duration
  extendVipDuration: {
    mutationFn: ({ recordId, duration }) =>
      cmd.EXTEND_VIP_DURATION({
        payload: { record_id: recordId, duration },
        throwRouteError: false,
      }),
  },

  // Revoke all VIP for a specific player
  revokeAllVip: {
    mutationFn: (playerId) =>
      cmd.REVOKE_ALL_VIP({
        payload: { player_id: playerId },
        throwRouteError: false,
      }),
  },

  // Synchronize with game server
  synchronizeWithGameServer: {
    mutationFn: () =>
      cmd.SYNCHRONIZE_WITH_GAME_SERVER({
        throwRouteError: false,
      }),
  },

  // Convert old-style VIP records into a VIP list
  convertOldStyleVipRecords: {
    mutationFn: ({ records, vipListId }) =>
      cmd.CONVERT_OLD_STYLE_VIP_RECORDS({
        payload: { records, vip_list_id: vipListId },
        throwRouteError: false,
      }),
  },
};