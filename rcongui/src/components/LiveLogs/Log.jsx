import { styled } from '@mui/material/styles';
import Line from "./LogLine"
import dayjs from 'dayjs';

export const TIME_FORMAT = 'HH:mm:ss, MMM DD';

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

export const actionToEmoji = {
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

export const Action = styled('span', {
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

const Log = ({ log }) => {
  const timestamp = dayjs(new Date(log.timestamp_ms)).format(TIME_FORMAT);

  return (
    <Line
      component={'pre'}
      tabIndex={-1}
      team={getTeamForLog(log)}
      severity={getLogSeverity(log)}
    >
      {timestamp}
      {`\t`}
      <Action type={log.action}>{log.action}</Action>
      {`\t`}
      {log.message}
    </Line>
  );
};

export default Log;
