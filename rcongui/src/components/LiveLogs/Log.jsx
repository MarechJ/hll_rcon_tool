import { Typography } from '@mui/material';
import { blue, grey, orange, red } from '@mui/material/colors';
import { styled, darken, lighten } from '@mui/material/styles';
import moment from 'moment';

/*
>>> LOG ACTION TYPES <<<

"ADMIN",
"ADMIN BANNED",
"ADMIN KICKED",
"ADMIN MISC",
"CAMERA",
"CHAT",
"CHAT[Allies]",
"CHAT[Allies][Team]",
"CHAT[Allies][Unit]",
"CHAT[Axis]",
"CHAT[Axis][Team]",
"CHAT[Axis][Unit]",
"CONNECTED",
"DISCONNECTED",
"KILL",
"MATCH",
"MATCH ENDED",
"MATCH START",
"MESSAGE",
"TEAM KILL",
"TEAMSWITCH",
"TK AUTO",
"TK AUTO BANNED",
"TK AUTO KICKED",
"VOTE",
"VOTE COMPLETED",
"VOTE EXPIRED",
"VOTE STARTED"
*/

const TIME_FORMAT = 'HH:mm:ss, MMM DD';

const getTeamColor = (team) => {
  switch (team) {
    case 'Allies':
      return blue['600'];
    case 'Axis':
      return red['600'];
    default:
      return grey['600'];
  }
};

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

const getLineBgColor = (severity, theme) => {
  const mode = theme.palette.mode;
  switch (severity) {
    case 'info':
    case 'warning':
      return theme.palette[severity][mode];
  }
};

const getLineTextColor = (severity, theme, team) => {
  const mode = theme.palette.mode;
  switch (severity) {
    case 'info':
    case 'warning':
      return theme.palette.getContrastText(theme.palette[severity][mode]);
    case 'chat':
      const teamColor = getTeamColor(team);
      return mode === 'light' ? darken(teamColor, 0.2) : lighten(teamColor, 0.5);
    default:
      return mode === 'light'
        ? darken(theme.palette.background.paper, 0.2)
        : lighten(theme.palette.background.paper, 0.2);
  }
};

export const Line = styled(Typography, {
  shouldForwardProp: (prop) => prop !== 'team' && prop !== 'severity',
})(({ theme, team, severity }) => ({
  borderLeftWidth: '4px',
  borderLeftColor: getTeamColor(team),
  borderLeftStyle: 'solid',
  paddingLeft: theme.spacing(0.5),
  tabSize: 2,
  fontFamily: 'monospace',
  fontSize: '0.8em',
  margin: 0,
  '&:hover, &:focus': {
    background: theme.palette.action.hover,
  },
  '.highlighted &': {
    color: getLineTextColor(severity, theme, team),
    background: getLineBgColor(severity, theme),
    fontWeight: severity !== 'normal' && 'bold',
  }
}));

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

const Log = ({ log }) => {
  const timestamp = moment(new Date(log.timestamp_ms)).format(TIME_FORMAT);

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