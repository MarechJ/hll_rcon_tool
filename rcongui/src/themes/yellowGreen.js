import { createTheme, adaptV4Theme } from '@mui/material/styles';

const YellowGreenTheme = createTheme(adaptV4Theme({
  palette: {
    secondary: {
      light: '#5edfca',
      main: '#17ad99',
      dark: '#007d6b',
    },
    primary: {
      light: '#ffe54c',
      main: '#ffb300',
      dark: '#c68400',
    },
  },
}));

export default YellowGreenTheme;
