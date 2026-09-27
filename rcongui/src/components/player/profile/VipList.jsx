import { Chip, Stack, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { usePlayerVipRecords } from "@/hooks/usePlayerVipRecords";
import { vipListQueryOptions } from "@/queries/vip-list-query";

const VipList = ({ playerId, vip, otherVips = [] }) => {
  const { records, canView, isPending, isError } = usePlayerVipRecords(playerId);
  const { data: lists = [] } = useQuery({
    ...vipListQueryOptions.lists(),
    enabled: canView && records.length > 0,
  });
  const gameserverVips = [vip, ...otherVips].filter(Boolean);

  return (
    <Stack spacing={1}>
      {canView && isPending && <Typography>Loading VIP list records…</Typography>}
      {canView && isError && <Typography>VIP list records unavailable</Typography>}
      {records.map((record) => {
        const status = record.is_expired ? "Expired" : record.is_active ? "Active" : "Inactive";
        return (
          <Stack key={record.id} direction="row" alignItems="center" flexWrap="wrap" gap={1}>
            <Typography variant="body2">
              {lists.find((list) => list.id === record.vip_list_id)?.name ?? `VIP list #${record.vip_list_id}`}
            </Typography>
            <Chip size="small" label={status} color={status === "Active" ? "success" : "default"} />
            <Typography variant="body2" color="text.secondary">
              {record.expires_at ? `Until ${dayjs(record.expires_at).format("LLL")}` : "Never expires"}
            </Typography>
          </Stack>
        );
      })}
      {gameserverVips.map((entry, index) => (
        <Stack key={`${entry.server_number}-${index}`} direction="row" alignItems="center" flexWrap="wrap" gap={1}>
          <Typography variant="body2">Legacy CRCON VIP record #{entry.server_number}</Typography>
          <Chip size="small" label={entry.expiration && dayjs(entry.expiration).isBefore(dayjs()) ? "Expired" : "Stored"} variant="outlined" />
          <Typography variant="body2" color="text.secondary">
            {entry.expiration ? `Stored expiration: ${dayjs(entry.expiration).format("LLL")}` : "No stored expiration"}
          </Typography>
        </Stack>
      ))}
      {gameserverVips.length > 0 && (
        <Typography variant="caption" color="text.secondary">
          Legacy CRCON dates are stored separately from VIP lists and may be outdated. They are not live gameserver expiration dates.
        </Typography>
      )}
      {canView && !isPending && !isError && records.length === 0 && gameserverVips.length === 0 && (
        <Typography>No VIP records found</Typography>
      )}
      {!canView && gameserverVips.length === 0 && (
        <Typography>VIP list records are not available with your permissions</Typography>
      )}
    </Stack>
  );
};

export default VipList;
