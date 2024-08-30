import { createTheme } from '@mui/material';

const GreenYellowDarkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      light: '#5edfca',
      main: '#17ad99',
      dark: '#007d6b',
    },
    secondary: {
      light: '#ffe54c',
      main: '#ffb300',
      dark: '#c68400',
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

export default GreenYellowDarkTheme;
