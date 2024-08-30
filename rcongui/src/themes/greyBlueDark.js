import { createTheme } from '@mui/material';

const GreyBlueDarkTheme = createTheme({
  editor: 'vs-dark',
  palette: {
    mode: 'dark',
    primary: {
      light: '#8eacbb',
      main: '#607d8b',
      dark: '#34515e',
    },
    secondary: {
      light: '#c3fdff',
      main: '#90caf9',
      dark: '#5d99c6',
    },
    background: {
      default: '#303030',
      paper: '#424242',
    },
    text: {
      primary: '#fff',
      secondary: ' rgba(255, 255, 255, 0.7)',
      disabled: 'rgba(255, 255, 255, 0.5)',
    },
  },
});

export default GreyBlueDarkTheme;
