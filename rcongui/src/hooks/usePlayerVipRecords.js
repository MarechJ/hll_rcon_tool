import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { vipListQueryOptions } from "@/queries/vip-list-query";

export function usePlayerVipRecords(playerId, enabled = true) {
  const { permissions } = useAuth();
  const canView = Boolean(
    permissions?.is_superuser ||
      permissions?.permissions?.some((entry) => entry.permission === "can_view_vip_lists")
  );
  const records = useQuery({
    ...vipListQueryOptions.playerRecords(playerId),
    enabled: canView && Boolean(playerId) && enabled,
  });
  return { ...records, canView, records: records.data ?? [] };
}
