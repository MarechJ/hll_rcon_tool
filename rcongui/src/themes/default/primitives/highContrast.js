import { createTheme, alpha } from '@mui/material/styles';

const defaultTheme = createTheme();

const customShadows = [...defaultTheme.shadows];

export const brand = {
  50: 'hsl(211, 100%, 98%)',   // Even lighter blue for better contrast
  100: 'hsl(211, 100%, 95%)',  // Very light blue
  200: 'hsl(211, 100%, 90%)',  // Light blue
  300: 'hsl(211, 100%, 75%)',  // Medium light blue
  400: 'hsl(211, 100%, 55%)',  // Bright blue (#0366d6) - made brighter
  500: 'hsl(211, 100%, 45%)',  // Medium blue
  600: 'hsl(211, 100%, 35%)',  // Medium dark blue
  700: 'hsl(211, 100%, 25%)',  // Dark blue
  800: 'hsl(211, 100%, 18%)',  // Very dark blue
  900: 'hsl(211, 100%, 12%)',  // Darkest blue
};

export const gray = {
  50: 'hsl(210, 25%, 99%)',    // Almost white (#fafbfc)
  100: 'hsl(210, 24%, 95%)',   // Very light (#f0f3f6)
  200: 'hsl(210, 16%, 90%)',   // Light border (#dde1e5)
  300: 'hsl(210, 13%, 80%)',   // Muted (#a9b2bb)
  400: 'hsl(210, 12%, 65%)',   // Secondary text - lighter
  500: 'hsl(210, 11%, 40%)',   // Primary text - darker
  600: 'hsl(210, 18%, 25%)',   // Dark text (#1b1f23)
  700: 'hsl(210, 22%, 20%)',   // Dark background
  800: 'hsl(210, 25%, 12%)',   // Darker background
  900: 'hsl(210, 25%, 5%)',    // Darkest background
};

export const green = {
  50: 'hsl(140, 100%, 98%)',   // Lightest
  100: 'hsl(140, 70%, 95%)',   // Very light
  200: 'hsl(140, 70%, 90%)',   // Light (#85e89d)
  300: 'hsl(140, 70%, 80%)',   // Medium light
  400: 'hsl(140, 70%, 55%)',   // Bright (#34d058)
  500: 'hsl(140, 70%, 35%)',   // Medium (#28a745)
  600: 'hsl(140, 70%, 25%)',   // Medium dark
  700: 'hsl(140, 70%, 20%)',   // Dark
  800: 'hsl(140, 70%, 15%)',   // Very dark
  900: 'hsl(140, 70%, 8%)',    // Darkest
};

export const red = {
  50: 'hsl(360, 100%, 98%)',   // Lightest
  100: 'hsl(360, 100%, 95%)',  // Very light
  200: 'hsl(360, 100%, 90%)',  // Light
  300: 'hsl(360, 90%, 80%)',   // Medium light (#f97583)
  400: 'hsl(360, 85%, 65%)',   // Bright (#ea4a5a)
  500: 'hsl(360, 80%, 45%)',   // Medium (#cb2431)
  600: 'hsl(360, 75%, 35%)',   // Medium dark
  700: 'hsl(360, 75%, 25%)',   // Dark
  800: 'hsl(360, 75%, 15%)',   // Very dark
  900: 'hsl(360, 75%, 10%)',   // Darkest
};

export const orange = {
  50: 'hsl(40, 100%, 98%)',    // Lightest
  100: 'hsl(40, 100%, 95%)',   // Very light
  200: 'hsl(40, 100%, 90%)',   // Light
  300: 'hsl(40, 100%, 80%)',   // Medium light (#ffea7f)
  400: 'hsl(40, 100%, 70%)',   // Bright (#ffdf5d)
  500: 'hsl(40, 100%, 40%)',   // Medium (#b08800)
  600: 'hsl(40, 100%, 30%)',   // Medium dark
  700: 'hsl(40, 100%, 25%)',   // Dark
  800: 'hsl(40, 100%, 18%)',   // Very dark
  900: 'hsl(40, 100%, 12%)',   // Darkest
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
  default: {
    palette: {
      mode: 'light',
      common: {
        black: '#000',
        white: '#fff',
      },
      primary: {
        light: brand[300],
        main: brand[500],  // Darker main color for better contrast
        dark: brand[700],
        contrastText: '#fff',
      },
      secondary: {
        light: gray[200],
        main: gray[600],  // Darker for better contrast
        dark: gray[800],
        contrastText: '#fff',
      },
      info: {
        light: brand[200],
        main: brand[500],  // Darker for better visibility
        dark: brand[700],
        contrastText: '#fff',
      },
      warning: {
        light: orange[200],
        main: orange[500],  // Darker orange for better contrast
        dark: orange[700],
        contrastText: '#000',  // Black text on orange for better readability
      },
      error: {
        light: red[200],
        main: red[500],  // Darker red for better contrast
        dark: red[700],
        contrastText: '#fff',
      },
      success: {
        light: green[200],
        main: green[500],  // Darker green for better contrast
        dark: green[700],
        contrastText: '#fff',
      },
      grey: gray,
      divider: alpha(gray[400], 0.5),  // More visible divider
      background: {
        default: '#ffffff',  // Pure white background
        paper: gray[50],     // Very light gray for subtle contrast
      },
      text: {
        primary: gray[800],   // Very dark gray for maximum contrast
        secondary: gray[600], // Darker secondary text
        disabled: alpha(gray[800], 0.5),
      },
      action: {
        active: alpha(gray[900], 0.7),    // More visible active state
        hover: alpha(gray[200], 0.3),
        selected: alpha(gray[300], 0.4),   // More visible selected state
        disabled: alpha(gray[900], 0.4),   // More visible disabled state
        disabledBackground: alpha(gray[200], 0.5),
        focus: alpha(gray[300], 0.4),
      },
    },
  },
  dark: {
    palette: {
      mode: 'dark',
      common: {
        black: '#000',
        white: '#fff',
      },
      primary: {
        light: brand[300],
        main: brand[400],     // Brighter in dark mode
        dark: brand[600],
        contrastText: '#fff',
      },
      secondary: {
        light: gray[300],
        main: gray[400],      // Lighter in dark mode
        dark: gray[600],
        contrastText: '#000',
      },
      info: {
        light: brand[300],
        main: brand[400],     // Brighter for dark mode
        dark: brand[600],
        contrastText: '#fff',
      },
      warning: {
        light: orange[300],
        main: orange[400],    // Brighter orange for dark mode
        dark: orange[600],
        contrastText: '#000',
      },
      error: {
        light: red[300],
        main: red[400],       // Brighter red for dark mode
        dark: red[600],
        contrastText: '#fff',
      },
      success: {
        light: green[300],
        main: green[400],     // Brighter green for dark mode
        dark: green[600],
        contrastText: '#000',
      },
      grey: gray,
      divider: alpha(gray[400], 0.3),
      background: {
        default: gray[900],   // Very dark background
        paper: gray[800],     // Slightly lighter than default
      },
      text: {
        primary: '#fff',      // Pure white text
        secondary: gray[200], // Very light gray for secondary
        disabled: alpha('#fff', 0.5),
      },
      action: {
        active: alpha('#fff', 0.8),     // Very visible active state
        hover: alpha(gray[600], 0.3),
        selected: alpha(gray[600], 0.4),
        disabled: alpha('#fff', 0.3),
        disabledBackground: alpha(gray[800], 0.5),
        focus: alpha(gray[600], 0.4),
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