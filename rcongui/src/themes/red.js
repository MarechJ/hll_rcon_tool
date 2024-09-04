import { createTheme, adaptV4Theme } from '@mui/material/styles';

const RedTheme = createTheme(adaptV4Theme({
  palette: {
    primary: {
      light: '#ff7961',
      main: '#f44336',
      dark: '#ba000d',
    },
    secondary: {
      light: '#708690',
      main: '#445963',
      dark: '#1b3039',
    },
  },
}));

export default RedTheme;
