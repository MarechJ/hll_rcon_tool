import { createTheme, adaptV4Theme } from '@mui/material/styles';

const hll = createTheme(adaptV4Theme({
  palette: {
    primary: {
      light: '#484848',
      main: '#212121',
      dark: '#000000',
    },
    secondary: {
      light: '#ffac42',
      main: '#f47b00',
      dark: '#ba4c00',
    },
    background: {
      default: '#343434',
      paper: '#5b5b5b',
    },
    text: {
      primary: '#ffffff',
      secondary: ' rgba(0, 0, 0, 0.7)',
      disabled: 'rgba(0, 0, 0, 0.5)',
    },
  },
  components: {
    MuiChip: {
      styleOverrides: {
        deleteIcon: {
          color: '#212121',
        },
      },
    },
    MuiCssBaseline: {
      styleOverrides: {
        '@global': {
          body: {
            backgroundRepeat: 'no-repeat',
            backgroundAttachment: 'fixed',
            backgroundSize: 'cover',
            backgroundImage: 'url("hll.jpg")',
          },
        },
      },
    },
  },
}));

export default hll;
