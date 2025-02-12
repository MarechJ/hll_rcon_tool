import { cmd } from "@/utils/fetchUtils";
import { queryOptions } from "@tanstack/react-query";
import { queryClient } from "@/queryClient";

export const vipQueryKeys = {
  list: [{ queryIdentifier: "get_vip_ids" }],
  add: [{ queryIdentifier: "add_vip" }],
  remove: [{ queryIdentifier: "remove_vip" }],
};

export const vipQueryOptions = {
  list: () =>
    queryOptions({
      queryKey: vipQueryKeys.list,
      queryFn: () => cmd.GET_VIPS(),
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
};
