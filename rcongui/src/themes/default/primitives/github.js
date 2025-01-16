import { createTheme, alpha } from '@mui/material/styles';

const defaultTheme = createTheme();

const customShadows = [...defaultTheme.shadows];

export const brand = {
  50: 'hsl(211, 100%, 97%)',  // Lightest blue
  100: 'hsl(211, 100%, 93%)', // Light blue
  200: 'hsl(211, 100%, 85%)', // Blue highlight
  300: 'hsl(211, 100%, 71%)', // Secondary blue
  400: 'hsl(211, 100%, 50%)', // Primary blue (#0366d6)
  500: 'hsl(211, 100%, 42%)', // Darker blue
  600: 'hsl(211, 100%, 35%)', // Deep blue
  700: 'hsl(211, 100%, 27%)', // Very dark blue
  800: 'hsl(211, 100%, 20%)', // Darkest blue
  900: 'hsl(211, 100%, 15%)', // Navy blue
};

export const gray = {
  50: 'hsl(210, 25%, 98%)',   // Lightest (#f6f8fa)
  100: 'hsl(210, 24%, 93%)',  // Light (#e1e4e8)
  200: 'hsl(210, 16%, 85%)',  // Border (#d1d5da)
  300: 'hsl(210, 13%, 72%)',  // Muted (#959da5)
  400: 'hsl(210, 12%, 58%)',  // Secondary text
  500: 'hsl(210, 11%, 43%)',  // Primary text
  600: 'hsl(210, 18%, 30%)',  // Dark text (#24292e)
  700: 'hsl(210, 22%, 23%)',  // Dark background
  800: 'hsl(210, 25%, 15%)',  // Darker background
  900: 'hsl(210, 25%, 8%)',   // Darkest background
};

export const green = {
  50: 'hsl(140, 100%, 97%)',  // Lightest
  100: 'hsl(140, 60%, 93%)',  // Light
  200: 'hsl(140, 60%, 85%)',  // (#85e89d)
  300: 'hsl(140, 60%, 75%)',  // 
  400: 'hsl(140, 60%, 50%)',  // (#34d058)
  500: 'hsl(140, 60%, 38%)',  // (#28a745)
  600: 'hsl(140, 60%, 30%)',  // 
  700: 'hsl(140, 60%, 23%)',  // 
  800: 'hsl(140, 60%, 15%)',  // 
  900: 'hsl(140, 60%, 8%)',   // 
};

export const red = {
  50: 'hsl(360, 100%, 97%)',  // Lightest
  100: 'hsl(360, 90%, 93%)',  // Light
  200: 'hsl(360, 90%, 85%)',  // 
  300: 'hsl(360, 85%, 75%)',  // (#f97583)
  400: 'hsl(360, 80%, 60%)',  // (#ea4a5a)
  500: 'hsl(360, 75%, 50%)',  // (#cb2431)
  600: 'hsl(360, 70%, 40%)',  // 
  700: 'hsl(360, 70%, 30%)',  // 
  800: 'hsl(360, 70%, 20%)',  // 
  900: 'hsl(360, 70%, 10%)',  // 
};

export const orange = {
  50: 'hsl(40, 100%, 97%)',   // Lightest
  100: 'hsl(40, 100%, 92%)',  // Light
  200: 'hsl(40, 100%, 85%)',  // 
  300: 'hsl(40, 100%, 75%)',  // (#ffea7f)
  400: 'hsl(40, 100%, 68%)',  // (#ffdf5d)
  500: 'hsl(40, 100%, 35%)',  // (#b08800)
  600: 'hsl(40, 100%, 30%)',  // 
  700: 'hsl(40, 100%, 25%)',  // 
  800: 'hsl(40, 100%, 20%)',  // 
  900: 'hsl(40, 100%, 15%)',  // 
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
      primary: {
        light: brand[300],    // #79b8ff
        main: brand[400],     // #0366d6
        dark: brand[600],     // #044289
        contrastText: '#fff',
      },
      info: {
        light: brand[300],    // #79b8ff
        main: brand[400],     // #0366d6
        dark: brand[600],     // #044289
        contrastText: '#fff',
      },
      warning: {
        light: orange[300],   // #ffea7f
        main: orange[400],    // #ffdf5d
        dark: orange[500],    // #b08800
        contrastText: gray[800],
      },
      error: {
        light: red[300],      // #f97583
        main: red[400],       // #ea4a5a
        dark: red[500],       // #cb2431
        contrastText: '#fff',
      },
      success: {
        light: green[200],    // #85e89d
        main: green[400],     // #34d058
        dark: green[500],     // #28a745
        contrastText: '#fff',
      },
      grey: {
        ...gray,
      },
      divider: alpha(gray[200], 0.8),
      background: {
        default: '#fff',
        paper: gray[50],      // #f6f8fa
      },
      text: {
        primary: gray[600],   // #24292e
        secondary: gray[500], // #586069
        warning: orange[400], // #ffdf5d
      },
      action: {
        hover: alpha(gray[200], 0.4),
        selected: alpha(gray[200], 0.24),
      },
    },
  },
  dark: {
    palette: {
      primary: {
        light: brand[300],
        main: brand[400],
        dark: brand[600],
        contrastText: '#fff',
      },
      info: {
        light: brand[300],
        main: brand[400],
        dark: brand[600],
        contrastText: '#fff',
      },
      warning: {
        light: orange[300],
        main: orange[400],
        dark: orange[600],
        contrastText: gray[800],
      },
      error: {
        light: red[300],
        main: red[400],
        dark: red[600],
        contrastText: '#fff',
      },
      success: {
        light: green[300],
        main: green[400],
        dark: green[600],
        contrastText: '#fff',
      },
      grey: {
        ...gray,
      },
      divider: alpha(gray[700], 0.6),
      background: {
        default: gray[900],              // GitHub dark mode background
        paper: 'hsl(220, 30%, 7%)',      // GitHub dark mode surface
      },
      text: {
        primary: '#fff',
        secondary: gray[400],
      },
      action: {
        hover: alpha(gray[600], 0.2),
        selected: alpha(gray[600], 0.3),
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