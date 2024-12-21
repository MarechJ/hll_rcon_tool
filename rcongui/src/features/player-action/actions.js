import SportsMartialArtsIcon from "@mui/icons-material/SportsMartialArts";
import GavelIcon from "@mui/icons-material/Gavel";
import BlockIcon from "@mui/icons-material/Block";
import WarningIcon from "@mui/icons-material/Warning";
import SyncIcon from "@mui/icons-material/Sync";
import SyncLockIcon from "@mui/icons-material/SyncLock";
import RemoveRedEyeIcon from "@mui/icons-material/RemoveRedEye";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import MessageIcon from "@mui/icons-material/Message";
import StarIcon from "@mui/icons-material/Star";
import StarBorderIcon from "@mui/icons-material/StarBorder";
import FlagIcon from "@mui/icons-material/Flag";
import HowToRegIcon from "@mui/icons-material/HowToReg";
import AddCommentIcon from "@mui/icons-material/AddComment";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import { cmd, execute } from "@/utils/fetchUtils";
import { MessageFormFields } from "@/features/player-action/forms/MessageFormFields";
import { PunishFormFields } from "@/features/player-action/forms/PunishFormFields";
import { WatchFormFields } from "@/features/player-action/forms/WatchFormFields";
import { ConfirmationOnly } from "@/features/player-action/forms/ConfirmationOnly";
import { AddVipFormFields } from "@/features/player-action/forms/AddVipFormFields";
import { TempBanFormFields } from "@/features/player-action/forms/TempBanFormFields";
import { PermaBanFormFields } from "@/features/player-action/forms/PermaBanFormFields";
import { AddFlagFormFields } from "@/features/player-action/forms/AddFlagFormFields";
import { AddCommentFormFields } from "@/features/player-action/forms/AddCommentFormFields";
import { BlacklistPlayerFormFields } from "@/features/player-action/forms/BlacklistPlayerFields";
import { playerProfileQueryOptions } from "@/queries/player-profile-query";
import { RemoveFlagFormFields } from "./forms/RemoveFlagFormFields";
import { AddConsoleAdminFormFields } from "./forms/AddConsoleAdminFormFields";

const executeAction = (command) => async (payload) => {
  // In the UI, it does not make sense to ask for a reason and message
  // at the same time as they are the same thing. However, the API
  // expects both in the payload.
  if ("reason" in payload && command !== "message_player") {
    payload.message = payload.reason;
  }
  if ("player" in payload) {
    payload.name = payload.player;
  }
  // v10.x.x 'add_vip' change param from 'name' to 'description'
  if (command === "add_vip" || command === "add_admin") {
    payload.description = payload.player_name;
  }
  return await execute(command, payload);
};

// Define each action
export const messageAction = {
  name: "message",
  description: "Show message in top right corner of game interface.",
  component: MessageFormFields,
  icon: <MessageIcon />,
  execute: executeAction("message_player"),
  permission: ["can_message_players"],
};

export const watchAction = {
  name: "watch",
  description:
    "Send Discord message upon player connection (using webhook config).",
  component: WatchFormFields,
  icon: <RemoveRedEyeIcon />,
  execute: executeAction("watch_player"),
  permission: ["can_add_player_watch"],
};

export const removeWatchAction = {
  name: "remove Watch",
  description: "Remove from Watchlist.",
  component: ConfirmationOnly,
  icon: <VisibilityOffIcon color="warning" />,
  execute: executeAction("unwatch_player"),
  permission: ["can_remove_player_watch"],
};

export const vipAction = {
  name: "vip",
  description: "Add or Update VIP.",
  component: AddVipFormFields,
  icon: <StarIcon />,
  execute: executeAction("add_vip"),
  permission: ["can_add_vip"],
};

export const removeVipAction = {
  name: "Remove Vip",
  description: "Remove VIP.",
  component: ConfirmationOnly,
  icon: <StarBorderIcon color="warning" />,
  execute: executeAction("remove_vip"),
  permission: ["can_remove_vip"],
};

export const switchAction = {
  name: "switch",
  description: "Move player to opposite team.",
  component: ConfirmationOnly,
  icon: <SyncIcon />,
  execute: executeAction("switch_player_now"),
  permission: ["can_switch_players_immediately"],
};

export const switchOnDeathAction = {
  name: "switch on death",
  description: "Move player to opposite team upon death.",
  component: ConfirmationOnly,
  icon: <SyncLockIcon />,
  execute: executeAction("switch_player_on_death"),
  permission: ["can_switch_players_on_death"],
};

export const punishAction = {
  name: "punish",
  description: "Kill player in-game if alive.",
  component: PunishFormFields,
  icon: <WarningIcon />,
  execute: executeAction("punish"),
  permission: ["can_punish_players"],
};

export const kickAction = {
  name: "kick",
  description: "Remove player from server.",
  component: PunishFormFields,
  icon: <SportsMartialArtsIcon />,
  execute: executeAction("kick"),
  permission: ["can_kick_players"],
};

export const tempBanAction = {
  name: "tempBan",
  description: "Issue immediate temporary ban to player.",
  component: TempBanFormFields,
  icon: <GavelIcon />,
  execute: executeAction("temp_ban"),
  permission: ["can_temp_ban_players"],
  deprecated: true,
  deprecationNote:
    "We suggest utilizing blacklists for more effective ban management.",
};

export const permaBanAction = {
  name: "permaBan",
  description: "Initiate immediate indefinite ban to player.",
  component: PermaBanFormFields,
  icon: <BlockIcon />,
  execute: executeAction("perma_ban"),
  permission: ["can_perma_ban_players"],
  deprecated: true,
  deprecationNote:
    "We suggest utilizing blacklists for more effective ban management.",
};

export const blacklistAction = {
  name: "blacklist",
  description: "Add player to a blacklist.",
  component: BlacklistPlayerFormFields,
  icon: <AccountBalanceIcon />,
  execute: executeAction("add_blacklist_record"),
  permission: ["can_add_blacklist_record"],
  context: [
    {
      type: "blacklists",
      getQuery: () => ({
        queryKey: ["get_blacklists"],
        queryFn: () => cmd.GET_BLACKLISTS({ throwRouteError: false }),
      }),
    },
  ],
};

export const flagAction = {
  name: "flag",
  description: "Assign a flag to the player.",
  component: AddFlagFormFields,
  icon: <FlagIcon />,
  execute: executeAction("flag_player"),
  permission: ["can_flag_player"],
};

export const unflagAction = {
  name: "Remove Flag",
  description: "Remove a flag from the player.",
  component: RemoveFlagFormFields,
  icon: <FlagIcon color="warning" />,
  execute: executeAction("unflag_player"),
  permission: ["can_unflag_player"],
  context: [
    {
      type: "profile",
      // This action is only available for a single recipient
      getQuery: (recipients) =>
        playerProfileQueryOptions(recipients[0].player_id, {
          throwRouteError: false,
        }),
    },
  ],
};

export const commentAction = {
  name: "comment",
  description: "Add a comment to the player profile.",
  component: AddCommentFormFields,
  icon: <AddCommentIcon />,
  execute: executeAction("post_player_comment"),
  permission: ["can_add_player_comments"],
};

export const clearAccountAction = {
  name: "clear",
  description: "Remove all bans associated with the player account.",
  component: ConfirmationOnly,
  icon: <HowToRegIcon />,
  execute: executeAction("unban"),
  permission: ["can_remove_perma_bans"],
};

export const addConsoleAdminAction = {
  name: "Add Admin",
  description: "Add a console admin to the player.",
  component: AddConsoleAdminFormFields,
  icon: <AdminPanelSettingsIcon />,
  execute: executeAction("add_admin"),
  permission: ["can_add_admin_roles"],
  context: [
    {
      type: "admin_groups",
      getQuery: () => ({
        queryKey: ["get_admin_groups"],
        queryFn: () => cmd.GET_CONSOLE_ADMIN_GROUPS({ throwRouteError: false }),
      }),
    },
  ],
};

/**
 * Generate player actions based on the given parameters.
 * @param {Object} params - The parameters for generating player actions.
 * @param {boolean} [params.multiAction=false] - Whether these actions are applied to multiple players.
 * @param {boolean} [params.onlineAction=false] - Whether these actions are applied to online players.
 * @returns {Array} An array of player actions.
 */
export const generatePlayerActions = (
  { multiAction = false, onlineAction = false } = {
    multiAction: false,
    onlineAction: false,
  }
) => {
  const profileActions = multiAction
    ? [
        watchAction,
        removeWatchAction,
        vipAction,
        removeVipAction,
        blacklistAction,
        tempBanAction,
        permaBanAction,
        clearAccountAction,
        flagAction,
        commentAction,
        addConsoleAdminAction,
      ]
    : [
        watchAction,
        removeWatchAction,
        vipAction,
        removeVipAction,
        blacklistAction,
        tempBanAction,
        permaBanAction,
        clearAccountAction,
        flagAction,
        unflagAction,
        commentAction,
        addConsoleAdminAction,
      ];

  const gameActions = [
    messageAction,
    switchAction,
    switchOnDeathAction,
    punishAction,
    kickAction,
  ];

  const actions = onlineAction
    ? [...gameActions, ...profileActions]
    : profileActions;

  return actions;
};
