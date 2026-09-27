import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import MilitaryTechIcon from "@mui/icons-material/MilitaryTech";
import AssignmentIndIcon from "@mui/icons-material/AssignmentInd";
import {
  Badge,
  Box,
  Divider,
  ListItemIcon,
  Typography,
  Card,
  Tooltip,
} from "@mui/material";
import { useAuth } from "@/hooks/useAuth";
import { useActionDialog } from "@/hooks/useActionDialog";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import PersonIcon from "@mui/icons-material/Person";
import { useMemo, useState } from "react";
import { useEditAccountModal } from "@/hooks/useEditAccountModal";
import { useEditSoldierModal } from "@/hooks/useEditSoldierModal";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { usePlayerVipRecords } from "@/hooks/usePlayerVipRecords";
import { vipListMutationOptions, vipListQueryKeys, vipListQueryOptions } from "@/queries/vip-list-query";
import VipListRecordDialog from "@/components/VipList/VipListRecordDialog";
import { Actions } from "./actions";

/**
 * Displays a menu of actions that the user can perform on a player.
 * The provided actions are filtered based on the user's permissions.
 */
export function ActionMenu({
  actions,
  recipients,
  anchorEl,
  setAnchorEl,
  withProfile = false,
}) {
  const { permissions: user } = useAuth();
  const { openDialog } = useActionDialog();
  const { openWithId } = usePlayerSidebar();
  const open = Boolean(anchorEl);
  const [editingVipRecord, setEditingVipRecord] = useState(null);
  const queryClient = useQueryClient();
  const singlePlayer = !Array.isArray(recipients);
  const { records: vipRecords, canView: canViewVipLists, isPending: vipRecordsPending, isError: vipRecordsError } = usePlayerVipRecords(
    singlePlayer ? recipients.player_id : null, open || Boolean(editingVipRecord)
  );
  const canEditVipRecords = Boolean(
    user?.is_superuser || user?.permissions?.some((entry) => entry.permission === "can_change_vip_list_records")
  );
  const { data: vipLists = [] } = useQuery({
    ...vipListQueryOptions.lists(),
    enabled: canViewVipLists && vipRecords.length > 0,
  });
  const updateVipRecord = useMutation({
    ...vipListMutationOptions.editRecord,
    onSuccess: async (_result, data) => {
      setEditingVipRecord(null);
      toast.success("VIP record updated.");
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: [...vipListQueryKeys.playerRecords, recipients.player_id] }),
        queryClient.invalidateQueries({ queryKey: [...vipListQueryKeys.activeRecords, data.vipListId] }),
        queryClient.invalidateQueries({ queryKey: [...vipListQueryKeys.inactiveRecords, data.vipListId] }),
      ]);
    },
    onError: (error) => toast.error(error?.message ?? "The VIP record could not be updated."),
  });
  const { openModal: openAccountModal, modal: accountModal } =
    useEditAccountModal(recipients.player_id, recipients.account);
  const { openModal: openSoldierModal, modal: soldierModal } =
    useEditSoldierModal(recipients.player_id, recipients.soldier);
  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleActionClick = (action) => {
    openDialog(action, recipients);
    setAnchorEl(null);
  };

  const handleProfileClick = () => {
    handleClose();
    openWithId(recipients.player_id);
  };

  const filteredActionList = useMemo(
    () => actions.filter(hasPermission(user)),
    [actions, user]
  );

  return (
    <>
    <Menu
      id="long-menu"
      anchorEl={anchorEl}
      open={open}
      onClose={handleClose}
      sx={{ maxHeight: (theme) => theme.typography.pxToRem(500) }}
    >
      {withProfile && !Array.isArray(recipients) && (
        <>
          <MenuItem onClick={handleProfileClick} dense>
            <ListItemIcon>
              <PersonIcon />
            </ListItemIcon>
            View Profile
          </MenuItem>
          <MenuItem onClick={openSoldierModal} dense>
            <ListItemIcon>
              <MilitaryTechIcon />
            </ListItemIcon>
            Edit Soldier
          </MenuItem>
          <MenuItem onClick={openAccountModal} dense>
            <ListItemIcon>
              <AssignmentIndIcon />
            </ListItemIcon>
            Edit Account
          </MenuItem>
        </>
      )}
      {withProfile && !Array.isArray(recipients) && <Divider />}
      {singlePlayer && canEditVipRecords && vipRecords.map((record) => (
        <MenuItem
          key={`vip-record-${record.id}`}
          dense
          onClick={() => {
            setEditingVipRecord(record);
            handleClose();
          }}
        >
          Edit VIP record: {vipLists.find((list) => list.id === record.vip_list_id)?.name ?? `list #${record.vip_list_id}`}
        </MenuItem>
      ))}
      {filteredActionList.filter((action) =>
        action !== Actions.AddVIP || !singlePlayer || !canViewVipLists || (!vipRecordsPending && !vipRecordsError)
      ).map((action) => (
        <MenuItem
          key={action.name}
          onClick={(event) => handleActionClick(action, event)}
          dense
        >
          <ListItemIcon>
            <action.icon />
          </ListItemIcon>
          <Typography
            variant="inherit"
            sx={{ textDecoration: action.deprecated ? "line-through" : "" }}
          >
            {action === Actions.AddVIP && singlePlayer && vipRecords.length > 0
              ? "Add VIP to another list"
              : action.name[0].toUpperCase() + action.name.slice(1)}
          </Typography>
        </MenuItem>
      ))}
      {filteredActionList.length === 0 && (
        <MenuItem onClick={handleClose}>No actions available</MenuItem>
      )}
      {accountModal}
      {soldierModal}
    </Menu>
    {editingVipRecord && (
      <VipListRecordDialog
        open
        mode="edit"
        vipList={vipLists.find((list) => list.id === editingVipRecord.vip_list_id) ??
          { id: editingVipRecord.vip_list_id, name: `#${editingVipRecord.vip_list_id}` }}
        initialValues={{
          playerId: editingVipRecord.player_id,
          playerName: editingVipRecord.player_name,
          description: editingVipRecord.description,
          notes: editingVipRecord.notes,
          active: editingVipRecord.is_active,
          expiresAt: editingVipRecord.expires_at,
        }}
        loading={updateVipRecord.isPending}
        onClose={() => setEditingVipRecord(null)}
        onSubmit={(data) => updateVipRecord.mutateAsync({ id: editingVipRecord.id, ...data })}
      />
    )}
    </>
  );
}

/**
 * @typedef {Object} Player
 * @property {string} player_id - The unique identifier for the player
 * @property {string} name - The name of the player
 */

/**
 * @param {Player|Player[]} recipients - The player or players to perform actions on.
 * @param {ReactNode} renderButton - A custom button to render instead of the default one.
 * @param {boolean} withProfile - Whether to include a profile button in the menu.
 * @param {string} orientation - The orientation of the menu. Can be "vertical" or "horizontal".
 * @param {object} props - Additional props to pass to the menu button.
 */

/**
 * Displays a menu of actions that the user can perform on a player.
 * The provided actions are filtered based on the user's permissions.
 * If the withProfile prop is true, a profile button will be added to the menu.
 * The profile button will open the player sidebar with the player's id.
 */
export function ActionMenuButton({
  actions,
  recipients,
  renderButton,
  orientation = "vertical",
  withProfile = false,
  size = "regular",
  ...props
}) {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const buttonProps = {
    "aria-label": "more",
    id: "default-action-menu-button",
    "aria-controls": open ? "default-action-menu-button" : undefined,
    "aria-expanded": open ? "true" : undefined,
    "aria-haspopup": "true",
    onClick: handleClick,
  };

  return (
    <Box>
      {renderButton ? (
        renderButton({ ...buttonProps })
      ) : (
        <IconButton {...buttonProps} {...props}>
          <Badge
            badgeContent={Array.isArray(recipients) ? recipients.length : 0}
            color="primary"
          >
            {orientation === "vertical" ? <MoreVertIcon /> : <MoreHorizIcon />}
          </Badge>
        </IconButton>
      )}
      <ActionMenu
        actions={actions}
        recipients={recipients}
        withProfile={withProfile}
        anchorEl={anchorEl}
        setAnchorEl={setAnchorEl}
      />
    </Box>
  );
}

export function ActionBar({ actions, recipients = [] }) {
  return (
    <Card
      sx={{
        display: "flex",
        color: "text.secondary",
        p: 0,
        gap: 0,
        [`& .MuiIconButton-root`]: {
          borderRadius: 0,
          width: 40,
          height: 40,
        },
        [`& .MuiIconButton-root + .MuiIconButton-root`]: {
          borderLeft: (theme) => `1px solid ${theme.palette.divider}`,
        },
      }}
    >
      {actions.map((action) => (
        <ActionIconButton
          key={action.name}
          action={action}
          recipients={recipients}
        />
      ))}
    </Card>
  );
}

export function ActionIconButton({
  action,
  recipients,
  params,
  icon,
  label,
  sx,
  ...props
}) {
  const { permissions: user } = useAuth();
  const { openDialog } = useActionDialog();

  const handleActionClick = (action) => () => {
    openDialog(action, recipients, params);
  };

  return (
    <Tooltip title={label || action.name} key={action.name}>
      <span>
        <IconButton
          key={action.name}
          disabled={!hasPermission(user)}
          size="small"
          onClick={handleActionClick(action)}
          sx={{ opacity: action.deprecated ? 0.5 : 1 }}
          {...props}
        >
          {icon ? icon : <action.icon sx={sx} />}
        </IconButton>
      </span>
    </Tooltip>
  );
}

function hasPermission(user) {
  return (action) => {
    if (!user.is_superuser && action.permission) {
      // example ["can_blacklist", "can_watch", "can_ban", "can_message", "can_comment"]
      // user needs to have all permissions in the array
      return action.permission.every((perm) =>
        user.permissions.some((userPerm) => userPerm.permission === perm)
      );
    }

    return true;
  };
}
