import { Typography } from "@mui/material";
import { blue, grey, orange, red } from '@mui/material/colors';
import { styled, darken, lighten } from '@mui/material/styles';

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
  
  const LogLine = styled(Typography, {
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

  export default LogLine;