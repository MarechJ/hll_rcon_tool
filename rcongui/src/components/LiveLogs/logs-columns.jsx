import { styled } from '@mui/material/styles';
import dayjs from 'dayjs';

const TIME_FORMAT = 'HH:mm:ss, MMM DD';

const getTeamForLog = (log) => {
  let team;

  switch (log.action) {
    case 'KILL':
    case 'TEAM KILL':
      team = log.message.match(/\((?<team>Allies|Axis)\//)?.groups?.team;
      break;
    case 'TEAMSWITCH':
      team = log.message.match(/>\D(?<team>Allies|Axis)/)?.groups?.team;
      break;
    case 'CHAT':
    case 'CHAT[Allies]':
    case 'CHAT[Allies][Team]':
    case 'CHAT[Allies][Unit]':
    case 'CHAT[Axis]':
    case 'CHAT[Axis][Team]':
    case 'CHAT[Axis][Unit]':
      team = log.action.match(/(?<team>Allies|Axis)/)?.groups?.team;
      break;
    default:
      team = 'Unknown';
      break;
  }

  return team ?? 'Unknown';
};

const getLogSeverity = (log) => {
  switch (log.action) {
    case 'TEAM KILL':
    case 'TK AUTO':
    case 'TK AUTO BANNED':
    case 'TK AUTO KICKED':
    case 'ADMIN KICKED':
    case 'ADMIN BANNED':
      return 'warning';
    case 'ADMIN MISC':
    case 'CAMERA':
    case 'VOTE COMPLETED':
    case 'MESSAGE':
      return 'info';
    case 'CHAT':
    case 'CHAT[Allies]':
    case 'CHAT[Allies][Team]':
    case 'CHAT[Allies][Unit]':
    case 'CHAT[Axis]':
    case 'CHAT[Axis][Team]':
    case 'CHAT[Axis][Unit]':
      return 'chat';
    default:
      return 'normal';
  }
};

const actionToEmoji = {
  ADMIN: '🚨',
  'ADMIN MISC': '🚨',
  'ADMIN IDLE': '💤',
  'ADMIN ANTI-CHEAT': '🚷',
  'ADMIN BANNED': '⌛',
  'ADMIN PERMA BANNED': '⛔',
  'ADMIN KICKED': '🚷',
  CHAT: '💬',
  CAMERA: '👀',
  'CHAT[Allies]': '🟦',
  'CHAT[Allies][Team]': '🟦',
  'CHAT[Allies][Unit]': '🟦',
  'CHAT[Axis]': '🟥',
  'CHAT[Axis][Team]': '🟥',
  'CHAT[Axis][Unit]': '🟥',
  CONNECTED: '🛬',
  DISCONNECTED: '🛫',
  KILL: '💀',
  MATCH: '🏁',
  'MATCH ENDED': '🏁',
  'MATCH START': '🏁',
  MESSAGE: '📢',
  'TEAM KILL': '⚠️',
  TEAMSWITCH: '♻️',
  'TK AUTO': '🚷',
  'TK AUTO BANNED': '⌛',
  'TK AUTO KICKED': '🚷',
  VOTE: '🙋',
  'VOTE COMPLETED': '🙋',
  'VOTE EXPIRED': '🙋',
  'VOTE PASSED': '🙋',
  'VOTE STARTED': '🙋',
  UNKNOWN: '❓',
};

const Action = styled('span', {
  shouldForwardProp: (props) => props !== 'type',
})(({ theme, type }) => ({
  width: '16em',
  display: 'inline-block',
  '&::before': {
    content: `"${actionToEmoji[type] ?? actionToEmoji['UNKNOWN']}"`,
    display: 'inline-block',
    paddingRight: theme.spacing(1),
  },
}));

/*
 Log example: 
    {
        "version": 1,
        "timestamp_ms": 1729630418000,
        "event_time": "2024-10-22T20:53:38",
        "relative_time_ms": -1632.637,
        "raw": "[1.10 sec (1729630418)] DISCONNECTED HereCookie76152 (e520836e51d683d06f56e06e4cb74118)",
        "line_without_time": "DISCONNECTED HereCookie76152 (e520836e51d683d06f56e06e4cb74118)",
        "action": "DISCONNECTED",
        "player_name_1": "HereCookie76152",
        "player_id_1": "e520836e51d683d06f56e06e4cb74118",
        "player_name_2": null,
        "player_id_2": null,
        "weapon": null,
        "message": "HereCookie76152 (e520836e51d683d06f56e06e4cb74118)",
        "sub_content": null
    }

    or

    {
        "version": 1,
        "timestamp_ms": 1729629560000,
        "event_time": "2024-10-22T20:39:20",
        "relative_time_ms": -1363.4550000000002,
        "raw": "[1.00 sec (1729629560)] TEAM KILL: blanquartmael(Axis/76561199409157448) -> PeaceUndead(Axis/6d7e77a018bc9213cb1045ea67324367) with WALTHER P38",
        "line_without_time": "TEAM KILL: blanquartmael(Axis/76561199409157448) -> PeaceUndead(Axis/6d7e77a018bc9213cb1045ea67324367) with WALTHER P38",
        "action": "TEAM KILL",
        "player_name_1": "blanquartmael",
        "player_id_1": "76561199409157448",
        "player_name_2": "PeaceUndead",
        "player_id_2": "6d7e77a018bc9213cb1045ea67324367",
        "weapon": "WALTHER P38",
        "message": "blanquartmael(Axis/76561199409157448) -> PeaceUndead(Axis/6d7e77a018bc9213cb1045ea67324367) with WALTHER P38",
        "sub_content": null
    }
*/

const removePlayerIds = (message) => {
    // Combine both regex patterns into one
    return message.replace(/\((?:(?:Axis|Allies)\/)?(?:[0-9]{17}|[A-Z0-9]{16})\)/g, '');
};

// Column definitions for the log table
export const logColumns = [
    {
        header: 'Time',
        accessorKey: 'timestamp_ms',
        cell: ({ row }) => {
            return dayjs(row.original.timestamp_ms).format(TIME_FORMAT);
        },
    },
    {
        header: 'Action',
        accessorKey: 'action',
        cell: ({ row }) => {
            return <Action type={row.original.action}>{row.original.action}</Action>;
        },
    },
    {
        header: 'Message',
        accessorKey: 'message',
        // full width
        size: "100%",
        cell: ({ row }) => {
            return removePlayerIds(row.original.message);
        },
    },
];
