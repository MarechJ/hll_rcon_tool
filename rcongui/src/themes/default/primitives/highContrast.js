import { createTheme, alpha } from '@mui/material/styles';

const defaultTheme = createTheme();

const customShadows = [...defaultTheme.shadows];

export const brand = {
  50: 'hsl(0, 0%, 100%)',    // Pure white
  100: 'hsl(0, 0%, 96%)',
  200: 'hsl(0, 0%, 92%)',
  300: 'hsl(0, 0%, 87%)',
  400: 'hsl(0, 0%, 82%)',
  500: 'hsl(0, 0%, 77%)',    // Main variant
  600: 'hsl(0, 0%, 72%)',
  700: 'hsl(0, 0%, 67%)',
  800: 'hsl(0, 0%, 62%)',
  900: 'hsl(0, 0%, 57%)',
};

export const gray = {
  50: 'hsl(0, 0%, 100%)',    // Pure white
  100: 'hsl(0, 0%, 95%)',    // Very light gray
  200: 'hsl(0, 0%, 90%)',    // Light gray
  300: 'hsl(0, 0%, 80%)',    // Medium light gray
  400: 'hsl(0, 0%, 70%)',    // Medium gray
  500: 'hsl(0, 0%, 60%)',    // Medium dark gray
  600: 'hsl(0, 0%, 40%)',    // Dark gray
  700: 'hsl(0, 0%, 20%)',    // Very dark gray
  800: 'hsl(0, 0%, 10%)',    // Almost black
  900: 'hsl(0, 0%, 0%)',     // Pure black
};

export const green = {
  50: 'hsl(0, 0%, 96%)',     // Nearly white
  100: 'hsl(0, 0%, 92%)',
  200: 'hsl(0, 0%, 87%)',
  300: 'hsl(0, 0%, 82%)',
  400: 'hsl(0, 0%, 77%)',
  500: 'hsl(0, 0%, 72%)',    // Main variant
  600: 'hsl(0, 0%, 67%)',
  700: 'hsl(0, 0%, 62%)',
  800: 'hsl(0, 0%, 57%)',
  900: 'hsl(0, 0%, 52%)',
};

export const red = {
  50: 'hsl(0, 0%, 98%)',     // Nearly white
  100: 'hsl(0, 0%, 95%)',
  200: 'hsl(0, 0%, 90%)',
  300: 'hsl(0, 0%, 85%)',
  400: 'hsl(0, 0%, 80%)',
  500: 'hsl(0, 0%, 75%)',    // Main variant
  600: 'hsl(0, 0%, 70%)',
  700: 'hsl(0, 0%, 65%)',
  800: 'hsl(0, 0%, 60%)',
  900: 'hsl(0, 0%, 55%)',
};

export const orange = {
  50: 'hsl(0, 0%, 97%)',     // Nearly white
  100: 'hsl(0, 0%, 93%)',
  200: 'hsl(0, 0%, 88%)',
  300: 'hsl(0, 0%, 83%)',
  400: 'hsl(0, 0%, 78%)',
  500: 'hsl(0, 0%, 73%)',    // Main variant
  600: 'hsl(0, 0%, 68%)',
  700: 'hsl(0, 0%, 63%)',
  800: 'hsl(0, 0%, 58%)',
  900: 'hsl(0, 0%, 53%)',
};

export const yellow = {
  50: 'hsl(0, 0%, 99%)',     // Nearly white
  100: 'hsl(0, 0%, 94%)',
  200: 'hsl(0, 0%, 89%)',
  300: 'hsl(0, 0%, 84%)',
  400: 'hsl(0, 0%, 79%)',
  500: 'hsl(0, 0%, 74%)',    // Main variant
  600: 'hsl(0, 0%, 69%)',
  700: 'hsl(0, 0%, 64%)',
  800: 'hsl(0, 0%, 59%)',
  900: 'hsl(0, 0%, 54%)',
};

export const blue = {
  50: 'hsl(0, 0%, 95%)',     // Nearly white
  100: 'hsl(0, 0%, 91%)',
  200: 'hsl(0, 0%, 86%)',
  300: 'hsl(0, 0%, 81%)',
  400: 'hsl(0, 0%, 76%)',
  500: 'hsl(0, 0%, 71%)',    // Main variant
  600: 'hsl(0, 0%, 66%)',
  700: 'hsl(0, 0%, 61%)',
  800: 'hsl(0, 0%, 56%)',
  900: 'hsl(0, 0%, 51%)',
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
      common: {
        black: '#000',
        white: '#fff',
      },
      primary: {
        light: brand[400],     // Darker light shade
        main: brand[600],      // Darker main color
        dark: brand[800],      // Darker shade
        contrastText: '#fff',
      },
      secondary: {
        light: gray[500],      // Darker light gray
        main: gray[700],       // Darker medium gray
        dark: gray[900],       // Darkest gray
        contrastText: '#fff',
      },
      info: {
        light: brand[400],     // Darker light blue
        main: brand[600],      // Darker medium blue
        dark: brand[800],      // Darker blue
        contrastText: '#fff',
      },
      warning: {
        light: orange[400],    // Darker light orange
        main: orange[600],     // Darker medium orange
        dark: orange[800],     // Darker orange
        contrastText: '#000',
      },
      error: {
        light: red[400],       // Darker light red
        main: red[600],        // Darker medium red
        dark: red[800],        // Darker red
        contrastText: '#fff',
      },
      success: {
        light: green[400],     // Darker light green
        main: green[600],      // Darker medium green
        dark: green[800],      // Darker green
        contrastText: '#fff',
      },
      grey: gray,
      divider: alpha(gray[400], 0.4),
      background: {
        default: gray[50],     // Very light gray
        paper: gray[100],      // Light gray
      },
      text: {
        primary: gray[900],    // Very dark gray
        secondary: gray[700],  // Dark gray
        warning: orange[600],  // Darker warning text
        red: red[900],
        orange: orange[900],
        green: green[900],
        blue: blue[900],
      },
      action: {
        active: alpha(gray[900], 0.7),
        hover: alpha(gray[200], 0.3),
        selected: alpha(gray[300], 0.4),
        disabled: alpha(gray[900], 0.4),
        disabledBackground: alpha(gray[200], 0.5),
        focus: alpha(gray[300], 0.4),
      },
    },
  },
  dark: {
    palette: {
      common: {
        black: '#000',
        white: '#fff',
      },
      primary: {
        light: brand[300],
        main: brand[400],
        dark: brand[600],
        contrastText: '#fff',
      },
      secondary: {
        light: gray[300],
        main: gray[400],
        dark: gray[600],
        contrastText: '#000',
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
        contrastText: '#000',
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
        contrastText: '#000',
      },
      grey: gray,
      divider: alpha(gray[400], 0.3),
      background: {
        default: gray[900],
        paper: gray[800],
      },
      text: {
        primary: '#fff',
        secondary: gray[200],
        disabled: alpha('#fff', 0.5),
        red: red[400],
        orange: orange[400],
        green: green[400],
        blue: blue[400],
      },
      action: {
        active: alpha('#fff', 0.8),
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
    fontSize: defaultTheme.typography.pxToRem(16),
    lineHeight: 1.6,
  },
  body2: {
    fontSize: defaultTheme.typography.pxToRem(16),
    lineHeight: 1.6,
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