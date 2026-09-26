import { cmd } from "@/utils/fetchUtils";
import { queryOptions } from "@tanstack/react-query";
import { queryClient } from "@/queryClient";

export const vipQueryKeys = {
  list: [{ queryIdentifier: "get_vip_ids" }],
  add: [{ queryIdentifier: "add_vip" }],
  remove: [{ queryIdentifier: "remove_vip" }],
  syncPlan: [{ queryIdentifier: "get_vip_sync_plan" }],
  syncStatus: [{ queryIdentifier: "get_vip_sync_status" }],
  synchronize: [{ queryIdentifier: "synchronize_vip_lists" }],
  removeUnknown: [{ queryIdentifier: "remove_unknown_vip_from_gameserver" }],
};

export const vipQueryOptions = {
  list: () =>
    queryOptions({
      queryKey: vipQueryKeys.list,
      queryFn: () => cmd.GET_VIPS(),
    }),
  syncPlan: () =>
    queryOptions({
      queryKey: vipQueryKeys.syncPlan,
      queryFn: () =>
        cmd.GET_VIP_SYNC_PLAN({
          throwRouteError: false,
        }),
      enabled: false,
      retry: false,
    }),
  syncStatus: () =>
    queryOptions({
      queryKey: vipQueryKeys.syncStatus,
      queryFn: () =>
        cmd.GET_VIP_SYNC_STATUS({
          throwRouteError: false,
        }),
      refetchInterval: 10000,
      retry: false,
    }),
};

// const onMutationSuccess = (_, { player_id }) => {
//   queryClient.invalidateQueries({ queryKey: ["player", "profile", player_id] });
// };

export const vipMutationOptions = {
  add: {
    mutationKey: vipQueryKeys.add,
    mutationFn: ({ description, player_id, expiration, forward = false }) =>
      cmd.ADD_VIP({
        payload: { description, player_id, expiration, forward },
      }),
  },
  remove: {
    mutationKey: vipQueryKeys.remove,
    mutationFn: ({ player_id, forward = false }) =>
      cmd.DELETE_VIP({ payload: { player_id, forward } }),
  },
  synchronize: {
    mutationKey: vipQueryKeys.synchronize,
    mutationFn: () =>
      cmd.SYNCHRONIZE_VIP_LISTS({
        payload: {},
        throwRouteError: false,
      }),
  },
  removeUnknown: {
    mutationKey: vipQueryKeys.removeUnknown,
    mutationFn: ({ player_id }) =>
      cmd.REMOVE_UNKNOWN_VIP_FROM_GAMESERVER({
        payload: { player_id },
        throwRouteError: false,
      }),
  },
};
