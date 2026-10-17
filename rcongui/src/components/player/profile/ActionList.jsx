import { ActionIconButton } from "@/features/player-action/ActionMenu";
import { Actions } from "@/features/player-action/actions";
import { IconButton, Menu, MenuItem, Stack, Tooltip } from "@mui/material";
import StarIcon from "@mui/icons-material/Star";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "react-toastify";
import { useAuth } from "@/hooks/useAuth";
import { useGlobalStore } from "@/stores/global-state";
import {
  vipListMutationOptions,
  vipListQueryKeys,
  vipListQueryOptions,
} from "@/queries/vip-list-query";
import VipListRecordDialog from "@/components/VipList/VipListRecordDialog";
import { vipQueryOptions } from "@/queries/vip-query";
import { red, yellow } from "@mui/material/colors";

function ActionList({ playerProfile }) {
  const isWatched = playerProfile.is_watched;
  const isBlacklisted = playerProfile.is_blacklisted;
  const isBanned = playerProfile.is_banned;
  const { permissions } = useAuth();
  const queryClient = useQueryClient();
  const [editingRecord, setEditingRecord] = useState(null);
  const [recordMenuAnchor, setRecordMenuAnchor] = useState(null);
  const serverNumber = useGlobalStore((state) => state.status?.server_number);
  const canViewVipLists = Boolean(
    permissions?.is_superuser ||
    permissions?.permissions?.some((entry) => entry.permission === "can_view_vip_lists")
  );
  const canChangeVipRecords = Boolean(
    permissions?.is_superuser ||
    permissions?.permissions?.some((entry) => entry.permission === "can_change_vip_list_records")
  );
  const canViewGameserverVips = Boolean(
    permissions?.is_superuser ||
    permissions?.permissions?.some((entry) => entry.permission === "can_view_vip_ids")
  );
  const { data: gameserverVips, isError: gameserverVipError } = useQuery({
    ...vipQueryOptions.list(),
    enabled: canViewGameserverVips,
    staleTime: 30000,
  });
  const { data: vipRecords = [] } = useQuery({
    ...vipListQueryOptions.playerRecords(playerProfile.player_id, serverNumber),
    enabled: canViewVipLists && Boolean(playerProfile.player_id),
  });
  const { data: vipLists = [] } = useQuery({
    ...vipListQueryOptions.lists(),
    enabled: canChangeVipRecords && Boolean(editingRecord || recordMenuAnchor),
  });
  const editRecord = useMutation({
    ...vipListMutationOptions.editRecord,
    onSuccess: async (_result, data) => {
      setEditingRecord(null);
      toast.success("VIP record updated.");
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: [...vipListQueryKeys.playerRecords, playerProfile.player_id],
        }),
        queryClient.invalidateQueries({
          queryKey: [...vipListQueryKeys.activeRecords, data.vipListId],
        }),
        queryClient.invalidateQueries({
          queryKey: [...vipListQueryKeys.inactiveRecords, data.vipListId],
        }),
      ]);
    },
    onError: (error) => toast.error(error?.message ?? "The VIP record could not be updated."),
  });
  const openRecord = (event) => {
    if (!canChangeVipRecords) return;
    if (vipRecords.length === 1) {
      setEditingRecord(vipRecords[0]);
    } else {
      setRecordMenuAnchor(event.currentTarget);
    }
  };
  const activeListRecord = vipRecords.some(
    (record) => record.is_active && !record.is_expired
  );
  const hasListRecord = vipRecords.length > 0;
  const gameserverVip = Array.isArray(gameserverVips) &&
    gameserverVips.some((vip) => vip.player_id === playerProfile.player_id);
  const gameserverStatus = !canViewGameserverVips || gameserverVipError ||
    !Array.isArray(gameserverVips)
    ? "Gameserver VIP status unavailable"
    : gameserverVip
    ? "Gameserver VIP active"
    : "Gameserver VIP not active";
  const vipStatus = activeListRecord
    ? `VIP list record active; ${gameserverStatus}${canChangeVipRecords ? ". Click to edit." : ""}`
    : hasListRecord
    ? `VIP list record inactive or expired; ${gameserverStatus}${canChangeVipRecords ? ". Click to edit." : ""}`
    : gameserverVip
    ? "Gameserver VIP active; no active VIP list record"
    : "Add a VIP list record";
  return (
    <Stack direction="row" spacing={0.5}>
      {hasListRecord ? (
        <Tooltip title={vipStatus}>
          <IconButton
            onClick={openRecord}
            aria-disabled={!canChangeVipRecords}
            aria-label={canChangeVipRecords ? "Edit VIP list record" : vipStatus}
            sx={{ width: 40, height: 40 }}
          >
            <StarIcon sx={{ color: activeListRecord ? yellow["700"] : "text.disabled" }} />
          </IconButton>
        </Tooltip>
      ) : (
        <ActionIconButton
          action={Actions.AddVIP}
          label={vipStatus}
          recipients={[playerProfile]}
          sx={{
            opacity: gameserverVip ? 1 : 0.35,
            color: gameserverVip && yellow["700"],
            fontSize: "1.25rem",
          }}
        />
      )}
      <Menu
        anchorEl={recordMenuAnchor}
        open={Boolean(recordMenuAnchor)}
        onClose={() => setRecordMenuAnchor(null)}
      >
        {vipRecords.map((record) => (
          <MenuItem
            key={record.id}
            onClick={() => {
              setRecordMenuAnchor(null);
              setEditingRecord(record);
            }}
          >
            {vipLists.find((list) => list.id === record.vip_list_id)?.name ??
              `VIP list #${record.vip_list_id}`}
            {record.is_expired ? " · Expired" : record.is_active ? " · Active" : " · Inactive"}
          </MenuItem>
        ))}
      </Menu>
      {editingRecord && <VipListRecordDialog
        open
        mode="edit"
        vipList={vipLists.find((list) => list.id === editingRecord?.vip_list_id) ??
          (editingRecord ? { id: editingRecord.vip_list_id, name: `#${editingRecord.vip_list_id}` } : null)}
        initialValues={editingRecord ? {
          playerId: editingRecord.player_id,
          playerName: editingRecord.player_name,
          description: editingRecord.description,
          notes: editingRecord.notes,
          active: editingRecord.is_active,
          expiresAt: editingRecord.expires_at,
        } : undefined}
        loading={editRecord.isPending}
        onClose={() => setEditingRecord(null)}
        onSubmit={(data) => editRecord.mutateAsync({ id: editingRecord.id, ...data })}
      />}
      <ActionIconButton
        action={!isWatched ? Actions.AddWatch : Actions.RemoveWatch}
        recipients={[playerProfile]}
        sx={{ opacity: !isWatched ? 0.35 : 1, fontSize: "1.25rem" }}
      />
      <ActionIconButton
        action={Actions.AddBlacklist}
        recipients={[playerProfile]}
        sx={{
          opacity: !isBlacklisted ? 0.35 : 1,
          color: isBlacklisted && red["500"],
          fontSize: "1.25rem",
        }}
      />
      <ActionIconButton
        action={!isBanned ? Actions.TempBan : Actions.RemoveBan}
        recipients={[playerProfile]}
        sx={{
          opacity: !isBanned ? 0.35 : 1,
          color: isBanned && red["500"],
          fontSize: "1.25rem",
        }}
      />
    </Stack>
  );
}

export default ActionList;
