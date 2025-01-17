import { blue } from '@mui/material/colors';
import { createTheme, alpha } from '@mui/material/styles';

const defaultTheme = createTheme();

const customShadows = [...defaultTheme.shadows];

export const brand = {
  50: 'hsl(142.1, 76.2%, 97%)',  // Lightest primary
  100: 'hsl(142.1, 76.2%, 90%)',
  200: 'hsl(142.1, 76.2%, 80%)',
  300: 'hsl(142.1, 76.2%, 70%)',
  400: 'hsl(142.1, 76.2%, 60%)',
  500: 'hsl(142.1, 76.2%, 36.3%)', // --primary
  600: 'hsl(142.1, 76.2%, 30%)',
  700: 'hsl(142.1, 70.6%, 45.3%)', // dark mode primary
  800: 'hsl(144.9, 80.4%, 10%)',   // dark mode primary-foreground
  900: 'hsl(142.4, 71.8%, 29.2%)', // dark mode ring
};

export const gray = {
  50: 'hsl(0, 0%, 100%)',          // --background
  100: 'hsl(0, 0%, 98%)',          // --destructive-foreground
  200: 'hsl(240, 4.8%, 95.9%)',    // --secondary
  300: 'hsl(240, 5.9%, 90%)',      // --border
  400: 'hsl(240, 3.8%, 46.1%)',    // --muted-foreground
  500: 'hsl(240, 5.9%, 10%)',      // --secondary-foreground
  600: 'hsl(240, 10%, 3.9%)',      // --foreground
  700: 'hsl(240, 3.7%, 15.9%)',    // dark mode --border
  800: 'hsl(24, 9.8%, 10%)',       // dark mode --card
  900: 'hsl(20, 14.3%, 4.1%)',     // dark mode --background
};

export const green = {
  50: 'hsl(160, 60%, 97%)',
  100: 'hsl(160, 60%, 90%)',
  200: 'hsl(160, 60%, 80%)',
  300: 'hsl(160, 60%, 70%)',
  400: 'hsl(160, 60%, 45%)',       // --chart-2
  500: 'hsl(160, 60%, 40%)',
  600: 'hsl(160, 60%, 35%)',
  700: 'hsl(160, 60%, 30%)',
  800: 'hsl(160, 60%, 25%)',
  900: 'hsl(160, 60%, 20%)',
};

export const red = {
  50: 'hsl(0, 84.2%, 97%)',
  100: 'hsl(0, 84.2%, 90%)',
  200: 'hsl(0, 84.2%, 80%)',
  300: 'hsl(0, 84.2%, 70%)',
  400: 'hsl(0, 84.2%, 60.2%)',     // --destructive
  500: 'hsl(0, 62.8%, 30.6%)',     // dark mode --destructive
  600: 'hsl(0, 84.2%, 40%)',
  700: 'hsl(0, 84.2%, 30%)',
  800: 'hsl(0, 84.2%, 20%)',
  900: 'hsl(0, 84.2%, 10%)',
};

export const orange = {
  50: 'hsl(30, 80%, 97%)',
  100: 'hsl(30, 80%, 90%)',
  200: 'hsl(30, 80%, 80%)',
  300: 'hsl(30, 80%, 70%)',
  400: 'hsl(30, 80%, 55%)',        // --chart-3
  500: 'hsl(30, 80%, 45%)',
  600: 'hsl(30, 80%, 35%)',
  700: 'hsl(30, 80%, 30%)',
  800: 'hsl(30, 80%, 25%)',
  900: 'hsl(30, 80%, 20%)',
};

export const getDesignTokens = (mode) => {
  customShadows[1] =
    mode === 'dark'
      ? 'hsla(220, 30%, 5%, 0.7) 0px 4px 16px 0px, hsla(220, 25%, 10%, 0.8) 0px 8px 16px -5px'
      : 'hsla(220, 30%, 5%, 0.07) 0px 4px 16px 0px, hsla(220, 25%, 10%, 0.07) 0px 8px 16px -5px';

  return {
    palette: {
      mode,
      primary: {
        light: brand[200],
        main: brand[400],
        dark: brand[700],
        contrastText: brand[50],
        ...(mode === 'dark' && {
          contrastText: brand[50],
          light: brand[300],
          main: brand[400],
          dark: brand[700],
        }),
      },
      info: {
        light: brand[100],
        main: brand[300],
        dark: brand[600],
        contrastText: gray[50],
        ...(mode === 'dark' && {
          contrastText: brand[300],
          light: brand[500],
          main: brand[700],
          dark: brand[900],
        }),
      },
      warning: {
        light: orange[300],
        main: orange[400],
        dark: orange[800],
        ...(mode === 'dark' && {
          light: orange[400],
          main: orange[500],
          dark: orange[700],
        }),
      },
      error: {
        light: red[300],
        main: red[400],
        dark: red[800],
        ...(mode === 'dark' && {
          light: red[400],
          main: red[500],
          dark: red[700],
        }),
      },
      success: {
        light: green[300],
        main: green[400],
        dark: green[800],
        ...(mode === 'dark' && {
          light: green[400],
          main: green[500],
          dark: green[700],
        }),
      },
      grey: {
        ...gray,
      },
      divider: mode === 'dark' ? alpha(gray[700], 0.6) : alpha(gray[300], 0.4),
      background: {
        default: 'hsl(0, 0%, 99%)',
        paper: 'hsl(220, 35%, 97%)',
        ...(mode === 'dark' && { default: gray[900], paper: 'hsl(220, 30%, 7%)' }),
      },
      text: {
        primary: gray[800],
        secondary: gray[600],
        warning: orange[400],
        ...(mode === 'dark' && {
          primary: 'hsl(0, 0%, 100%)',
          secondary: gray[400],
        }),
      },
      action: {
        hover: alpha(gray[200], 0.2),
        selected: `${alpha(gray[200], 0.3)}`,
        ...(mode === 'dark' && {
          hover: alpha(gray[600], 0.2),
          selected: alpha(gray[600], 0.3),
        }),
      },
    },
    typography: {
      fontFamily: 'Inter, sans-serif',
      h1: {
        fontSize: defaultTheme.typography.pxToRem(48),
        fontWeight: 600,
        lineHeight: 1.2,
        letterSpacing: -0.5,
      },
      h2: {
        fontSize: defaultTheme.typography.pxToRem(36),
        fontWeight: 600,
        lineHeight: 1.2,
      },
      h3: {
        fontSize: defaultTheme.typography.pxToRem(30),
        lineHeight: 1.2,
      },
      h4: {
        fontSize: defaultTheme.typography.pxToRem(24),
        fontWeight: 600,
        lineHeight: 1.5,
      },
      h5: {
        fontSize: defaultTheme.typography.pxToRem(20),
        fontWeight: 600,
      },
      h6: {
        fontSize: defaultTheme.typography.pxToRem(18),
        fontWeight: 600,
      },
      subtitle1: {
        fontSize: defaultTheme.typography.pxToRem(18),
      },
      subtitle2: {
        fontSize: defaultTheme.typography.pxToRem(14),
        fontWeight: 500,
      },
      body1: {
        fontSize: defaultTheme.typography.pxToRem(14),
      },
      body2: {
        fontSize: defaultTheme.typography.pxToRem(14),
        fontWeight: 400,
      },
      caption: {
        fontSize: defaultTheme.typography.pxToRem(12),
        fontWeight: 400,
      },
    },
    shape: {
      borderRadius: 8,
    },
    shadows: customShadows,
  };
};

export const colorSchemes = {
  light: {
    palette: {
      mode: 'light',
      primary: {
        main: 'hsl(142.1, 76.2%, 36.3%)',      // --primary
        contrastText: 'hsl(355.7, 100%, 97.3%)', // --primary-foreground
      },
      secondary: {
        main: 'hsl(240, 4.8%, 95.9%)',         // --secondary
        contrastText: 'hsl(240, 5.9%, 10%)',    // --secondary-foreground
      },
      error: {
        main: 'hsl(0, 84.2%, 60.2%)',          // --destructive
        contrastText: 'hsl(0, 0%, 98%)',        // --destructive-foreground
      },
      info: {
        main: 'hsl(220, 70%, 50%)',            // --chart-1
        contrastText: '#fff',
      },
      success: {
        main: 'hsl(160, 60%, 45%)',            // --chart-2
        contrastText: '#fff',
      },
      warning: {
        main: 'hsl(30, 80%, 55%)',             // --chart-3
        contrastText: '#fff',
      },
      background: {
        default: 'hsl(0, 0%, 100%)',           // --background
        paper: 'hsl(0, 0%, 100%)',             // --card
      },
      text: {
        primary: 'hsl(240, 10%, 3.9%)',        // --foreground
        secondary: 'hsl(240, 3.8%, 46.1%)',    // --muted-foreground
        red: red[600],
        orange: orange[600],
        green: green[600],
        blue: blue[600],
      },
      divider: 'hsl(240, 5.9%, 90%)',          // --border
      action: {
        hover: 'hsla(240, 4.8%, 95.9%, 0.8)',  // --secondary with alpha
        selected: 'hsla(240, 4.8%, 95.9%, 0.6)', // --secondary with alpha
      },
    },
  },
  dark: {
    palette: {
      mode: 'dark',
      primary: {
        main: 'hsl(142.1, 70.6%, 45.3%)',      // --primary
        contrastText: 'hsl(144.9, 80.4%, 10%)', // --primary-foreground
      },
      secondary: {
        main: 'hsl(240, 3.7%, 15.9%)',         // --secondary
        contrastText: 'hsl(0, 0%, 98%)',        // --secondary-foreground
      },
      error: {
        main: 'hsl(0, 62.8%, 30.6%)',          // --destructive
        contrastText: 'hsl(0, 85.7%, 97.3%)',   // --destructive-foreground
      },
      info: {
        main: 'hsl(220, 70%, 50%)',            // --chart-1
        contrastText: '#fff',
      },
      success: {
        main: 'hsl(160, 60%, 45%)',            // --chart-2
        contrastText: '#fff',
      },
      warning: {
        main: 'hsl(30, 80%, 55%)',             // --chart-3
        contrastText: '#fff',
      },
      background: {
        default: 'hsl(20, 14.3%, 4.1%)',       // --background
        paper: 'hsl(24, 9.8%, 10%)',           // --card
      },
      text: {
        primary: 'hsl(0, 0%, 95%)',            // --foreground
        secondary: 'hsl(240, 5%, 64.9%)',      // --muted-foreground
        red: red[400],
        orange: orange[400],
        green: green[400],
        blue: blue[400],
      },
      divider: 'hsl(240, 3.7%, 15.9%)',        // --border
      action: {
        hover: 'hsla(12, 6.5%, 15.1%, 0.8)',   // --accent with alpha
        selected: 'hsla(12, 6.5%, 15.1%, 0.6)', // --accent with alpha
      },
    },
  },
};

export const typography = {
  fontFamily: 'Roboto, Inter, Arial, sans-serif',
  h1: {
    fontSize: defaultTheme.typography.pxToRem(48),
    fontWeight: 600,
    lineHeight: 1.2,
    letterSpacing: -0.5,
  },
  h2: {
    fontSize: defaultTheme.typography.pxToRem(36),
    fontWeight: 600,
    lineHeight: 1.2,
  },
  h3: {
    fontSize: defaultTheme.typography.pxToRem(30),
    lineHeight: 1.2,
  },
  h4: {
    fontSize: defaultTheme.typography.pxToRem(24),
    fontWeight: 600,
    lineHeight: 1.5,
  },
  h5: {
    fontSize: defaultTheme.typography.pxToRem(20),
    fontWeight: 600,
  },
  h6: {
    fontSize: defaultTheme.typography.pxToRem(18),
    fontWeight: 600,
  },
  subtitle1: {
    fontSize: defaultTheme.typography.pxToRem(18),
  },
  subtitle2: {
    fontSize: defaultTheme.typography.pxToRem(14),
    fontWeight: 500,
  },
  body1: {
    fontSize: defaultTheme.typography.pxToRem(14),
  },
  body2: {
    fontSize: defaultTheme.typography.pxToRem(14),
    fontWeight: 400,
  },
  caption: {
    fontSize: defaultTheme.typography.pxToRem(12),
    fontWeight: 400,
  },
};

export const shape = {
  borderRadius: 8,
};

const defaultShadows = [
  'none',
  'var(--template-palette-baseShadow)',
  ...defaultTheme.shadows.slice(2),
];

export const shadows = defaultShadows;