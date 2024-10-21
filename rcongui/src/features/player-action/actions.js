import SportsMartialArtsIcon from '@mui/icons-material/SportsMartialArts';
import GavelIcon from '@mui/icons-material/Gavel';
import BlockIcon from '@mui/icons-material/Block';
import WarningIcon from '@mui/icons-material/Warning';
import SyncIcon from '@mui/icons-material/Sync';
import SyncLockIcon from '@mui/icons-material/SyncLock';
import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye';
import MessageIcon from '@mui/icons-material/Message';
import StarIcon from '@mui/icons-material/Star';
import FlagIcon from '@mui/icons-material/Flag';
import HowToRegIcon from '@mui/icons-material/HowToReg';
import AddCommentIcon from '@mui/icons-material/AddComment';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import { execute } from '@/utils/fetchUtils';
import { MessageFormFields } from '@/features/player-action/forms/MessageFormFields';
import { PunishFormFields } from '@/features/player-action/forms/PunishFormFields';
import { WatchFormFields } from '@/features/player-action/forms/WatchFormFields';
import { ConfirmationOnly } from '@/features/player-action/forms/ConfirmationOnly';
import { AddVipFormFields } from '@/features/player-action/forms/AddVipFormFields';
import { TempBanFormFields } from '@/features/player-action/forms/TempBanFormFields';
import { PermaBanFormFields } from '@/features/player-action/forms/PermaBanFormFields';
import { AddFlagFormFields } from '@/features/player-action/forms/AddFlagFormFields';
import { AddCommentFormFields } from '@/features/player-action/forms/AddCommentFormFields';
import { BlacklistPlayerFormFields } from '@/features/player-action/forms/BlacklistPlayerFields';

const executeAction = (command) => async (payload) => {
    // In the UI, it does not make sense to ask for a reason and message
    // at the same time as they are the same thing. However, the API
    // expects both in the payload.
    if ('reason' in payload && command !== 'message_player') {
        payload.message = payload.reason;
    }
    if ('player' in payload) {
        payload.name = payload.player;
    }
    // v10.x.x 'add_vip' change param from 'name' to 'description'
    if (command === 'add_vip') {
        payload.description = payload.player_name;
    }
    return await execute(command, payload)
}

// Define each action
export const messageAction = {
    name: 'message',
    description: 'Show message in top right corner of game interface.',
    component: MessageFormFields,
    icon: <MessageIcon />,
    execute: executeAction('message_player'),
};

export const watchAction = {
    name: 'watch',
    description: 'Send Discord message upon player connection (using webhook config).',
    component: WatchFormFields,
    icon: <RemoveRedEyeIcon />,
    execute: executeAction('watch_player'),
};

export const vipAction = {
    name: 'vip',
    description: 'Manage VIP.',
    component: AddVipFormFields,
    icon: <StarIcon />,
    execute: executeAction('add_vip'),
};

export const switchAction = {
    name: 'switch',
    description: 'Move player to opposite team.',
    component: ConfirmationOnly,
    icon: <SyncIcon />,
    execute: executeAction('switch_player_now'),
};

export const switchOnDeathAction = {
    name: 'switch on death',
    description: 'Move player to opposite team upon death.',
    component: ConfirmationOnly,
    icon: <SyncLockIcon />,
    execute: executeAction('switch_player_on_death'),
};

export const punishAction = {
    name: 'punish',
    description: 'Kill player in-game if alive.',
    component: PunishFormFields,
    icon: <WarningIcon />,
    execute: executeAction('punish'),
};

export const kickAction = {
    name: 'kick',
    description: 'Remove player from server.',
    component: PunishFormFields,
    icon: <SportsMartialArtsIcon />,
    execute: executeAction('kick'),
};

export const tempBanAction = {
    name: 'tempBan',
    description: 'Issue immediate temporary ban to player.',
    component: TempBanFormFields,
    icon: <GavelIcon />,
    execute: executeAction('temp_ban'),
    deprecated: true,
    deprecationNote: "We suggest utilizing blacklists for more effective ban management.",
};

export const permaBanAction = {
    name: 'permaBan',
    description: 'Initiate immediate indefinite ban to player.',
    component: PermaBanFormFields,
    icon: <BlockIcon />,
    execute: executeAction('perma_ban'),
    deprecated: true,
    deprecationNote: "We suggest utilizing blacklists for more effective ban management.",
};

export const blacklistAction = {
    name: 'blacklist',
    description: 'Add player to a blacklist.',
    component: BlacklistPlayerFormFields,
    icon: <AccountBalanceIcon />,
    execute: executeAction('add_blacklist_record'),
    context: ["get_blacklists"],
}

export const flagAction = {
    name: 'flag',
    description: 'Assign a flag to the player.',
    component: AddFlagFormFields,
    icon: <FlagIcon />,
    execute: executeAction('flag_player'),
};

export const commentAction = {
    name: 'comment',
    description: 'Add a comment to the player profile.',
    component: AddCommentFormFields,
    icon: <AddCommentIcon />,
    execute: executeAction('post_player_comment'),
};

export const clearAccountAction = {
    name: 'clear',
    description: 'Remove all bans associated with the player account.',
    component: ConfirmationOnly,
    icon: <HowToRegIcon />,
    execute: executeAction('unban'),
};


// TODO
// A function that takes in either Player object or params as `hasVIP`
// and returns a list of relevant actions
// That will be used for a single recepient actions
// Or make it so that it makes sure all recepients are eligible for 
// that action
export const generatePlayerActions = (mode, player) => {
    // perhaps get whether is online or not based on the player
    switch (mode) {
        case 'profile':
            return playerProfileActions;
        case 'game':
            return playerGameActions;    
        default:
            throw new Error("Must provide either profile or game mode")
    }

}


export const playerProfileActions = [
    watchAction,
    vipAction,
    clearAccountAction,
    blacklistAction,
    tempBanAction,
    permaBanAction,
    flagAction,
    commentAction,
]

// The order of action objects here determins the order in the UI
export const playerGameActions = [
    messageAction,
    watchAction,
    vipAction,
    switchAction,
    switchOnDeathAction,
    punishAction,
    kickAction,
    blacklistAction,
    tempBanAction,
    permaBanAction,
    flagAction,
    commentAction,
];
