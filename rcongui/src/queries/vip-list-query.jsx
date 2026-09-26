import { queryOptions } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";

export const vipListQueryKeys = {
  lists: [{ queryIdentifier: "get_vip_lists" }],
  applicableLists: [{ queryIdentifier: "get_vip_lists_for_server" }],
  defaultList: [{ queryIdentifier: "get_default_vip_list" }],
  list: [{ queryIdentifier: "get_vip_list" }],
  activeRecords: [{ queryIdentifier: "get_active_vip_records" }],
  inactiveRecords: [{ queryIdentifier: "get_inactive_vip_records" }],
};

export const vipListQueryOptions = {
  lists: () =>
    queryOptions({
      queryKey: vipListQueryKeys.lists,
      queryFn: () => cmd.GET_VIP_LISTS(),
      select: (data) => (Array.isArray(data) ? data : []),
    }),

  applicableLists: (serverNumber) =>
    queryOptions({
      queryKey: [
        ...vipListQueryKeys.applicableLists,
        serverNumber ?? "current",
      ],
      queryFn: () =>
        cmd.GET_VIP_LISTS_FOR_SERVER(
          Number.isInteger(serverNumber)
            ? { params: { server_number: serverNumber } }
            : {}
        ),
      select: (data) => (Array.isArray(data) ? data : []),
    }),

  defaultList: (serverNumber) =>
    queryOptions({
      queryKey: [
        ...vipListQueryKeys.defaultList,
        serverNumber ?? "current",
      ],
      queryFn: () =>
        cmd.GET_DEFAULT_VIP_LIST(
          Number.isInteger(serverNumber)
            ? { params: { server_number: serverNumber } }
            : {}
        ),
    }),

  list: (vipListId) =>
    queryOptions({
      queryKey: [...vipListQueryKeys.list, vipListId],
      queryFn: () =>
        cmd.GET_VIP_LIST({
          params: { vip_list_id: vipListId },
        }),
      enabled: Number.isInteger(vipListId),
    }),

  activeRecords: (vipListId) =>
    queryOptions({
      queryKey: [...vipListQueryKeys.activeRecords, vipListId],
      queryFn: () =>
        cmd.GET_ACTIVE_VIP_RECORDS({
          params: { vip_list_id: vipListId },
        }),
      enabled: Number.isInteger(vipListId),
      select: (data) => (Array.isArray(data) ? data : []),
    }),

  inactiveRecords: (vipListId) =>
    queryOptions({
      queryKey: [...vipListQueryKeys.inactiveRecords, vipListId],
      queryFn: () =>
        cmd.GET_INACTIVE_VIP_RECORDS({
          params: { vip_list_id: vipListId },
        }),
      enabled: Number.isInteger(vipListId),
      select: (data) => (Array.isArray(data) ? data : []),
    }),
};

export const vipListMutationOptions = {
  createList: {
    mutationFn: (data) =>
      cmd.CREATE_VIP_LIST({
        payload: {
          name: data.name,
          servers: data.servers,
          sync: data.sync,
        },
        throwRouteError: false,
      }),
  },
  editList: {
    mutationFn: ({ id, ...data }) =>
      cmd.EDIT_VIP_LIST({
        payload: {
          vip_list_id: id,
          name: data.name,
          servers: data.servers,
          sync: data.sync,
        },
        throwRouteError: false,
      }),
  },
  setDefaultList: {
    mutationFn: ({ vipListId, serverNumber }) => {
      const payload = { vip_list_id: vipListId };

      if (Number.isInteger(serverNumber)) {
        payload.server_number = serverNumber;
      }

      return cmd.SET_DEFAULT_VIP_LIST({
        payload,
        throwRouteError: false,
      });
    },
  },
  clearDefaultList: {
    mutationFn: (serverNumber) => {
      const payload = {};

      if (Number.isInteger(serverNumber)) {
        payload.server_number = serverNumber;
      }

      return cmd.CLEAR_DEFAULT_VIP_LIST({
        payload,
        throwRouteError: false,
      });
    },
  },
  deleteList: {
    mutationFn: (vipList) =>
      cmd.DELETE_VIP_LIST({
        payload: { vip_list_id: vipList.id },
        throwRouteError: false,
      }),
  },
  createRecord: {
    mutationFn: (data) =>
      cmd.ADD_VIP_LIST_RECORD({
        payload: {
          player_id: data.playerId,
          vip_list_id: data.vipListId,
          description: data.description || null,
          active: data.active,
          expires_at:
            data.expiresAt?.toISOString?.() ??
            data.expiresAt ??
            null,
          notes: data.notes || null,
        },
        throwRouteError: false,
      }),
  },
  editRecord: {
    mutationFn: ({ id, ...data }) =>
      cmd.EDIT_VIP_LIST_RECORD({
        payload: {
          record_id: id,
          vip_list_id: data.vipListId,
          description: data.description || null,
          active: data.active,
          expires_at:
            data.expiresAt?.toISOString?.() ??
            data.expiresAt ??
            null,
          notes: data.notes || null,
        },
        throwRouteError: false,
      }),
  },
  deleteRecord: {
    mutationFn: (record) =>
      cmd.DELETE_VIP_LIST_RECORD({
        payload: { record_id: record.id },
        throwRouteError: false,
      }),
  },
  bulkEditRecords: {
    mutationFn: (data) => {
      const payload = {
        record_ids: data.recordIds,
      };

      if (data.vipListId !== undefined) {
        payload.vip_list_id = data.vipListId;
      }
      if (data.description !== undefined) {
        payload.description = data.description;
      }
      if (data.notes !== undefined) {
        payload.notes = data.notes;
      }
      if (data.active !== undefined) {
        payload.active = data.active;
      }
      if (data.expiresAt !== undefined) {
        payload.expires_at =
          data.expiresAt?.toISOString?.() ??
          data.expiresAt ??
          null;
      }

      return cmd.EDIT_VIP_LIST_RECORDS({
        payload,
        throwRouteError: false,
      });
    },
  },
  bulkDeleteRecords: {
    mutationFn: (recordIds) =>
      cmd.DELETE_VIP_LIST_RECORDS({
        payload: {
          record_ids: recordIds,
        },
        throwRouteError: false,
      }),
  },
};
