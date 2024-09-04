import { createTheme, adaptV4Theme } from '@mui/material/styles';

const GreenYellowLightTheme = createTheme(adaptV4Theme({
  palette: {
    mode: 'light',
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
  },
}));

export default GreenYellowLightTheme;
