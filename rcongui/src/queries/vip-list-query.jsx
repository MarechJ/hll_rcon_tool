import { queryOptions } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";

export const vipListQueryKeys = {
  lists: [{ queryIdentifier: "get_vip_lists" }],
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
};
