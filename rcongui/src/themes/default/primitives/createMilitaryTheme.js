import { alpha, createTheme } from "@mui/material/styles";

const defaultTheme = createTheme();

/**
 * Builds the shared tokens used by the two Hell Let Loose themes.
 *
 * Keeping the palette construction here makes the two themes easy to tune while
 * ensuring every semantic colour used by the UI is available in both modes.
 */
export default function createMilitaryTheme({
  brand,
  gray,
  green,
  orange,
  red,
  fontFamily,
  borderRadius,
  lightBackground,
  lightPaper,
  darkBackground,
  darkPaper,
}) {
  const colorSchemes = {
    light: {
      palette: {
        primary: {
          light: brand[300],
          main: brand[600],
          dark: brand[800],
          contrastText: brand[50],
        },
        info: {
          light: brand[200],
          main: brand[600],
          dark: brand[800],
          contrastText: brand[50],
        },
        warning: {
          light: orange[300],
          main: orange[500],
          dark: orange[800],
        },
        error: {
          light: red[300],
          main: red[600],
          dark: red[800],
        },
        success: {
          light: green[300],
          main: green[600],
          dark: green[800],
        },
        grey: { ...gray },
        divider: alpha(gray[500], 0.34),
        background: {
          default: lightBackground,
          paper: lightPaper,
        },
        text: {
          primary: gray[900],
          secondary: gray[700],
          warning: orange[700],
          red: red[700],
          orange: orange[700],
          green: green[700],
          blue: brand[700],
        },
        action: {
          hover: alpha(brand[300], 0.14),
          selected: alpha(brand[400], 0.22),
        },
        baseShadow:
          "hsla(45, 28%, 12%, 0.12) 0px 4px 16px 0px, hsla(45, 25%, 12%, 0.08) 0px 8px 16px -5px",
      },
    },
    dark: {
      palette: {
        primary: {
          light: brand[300],
          main: brand[400],
          dark: brand[700],
          contrastText: gray[900],
        },
        info: {
          light: brand[300],
          main: brand[400],
          dark: brand[700],
          contrastText: gray[900],
        },
        warning: {
          light: orange[300],
          main: orange[400],
          dark: orange[700],
        },
        error: {
          light: red[300],
          main: red[400],
          dark: red[700],
        },
        success: {
          light: green[300],
          main: green[400],
          dark: green[700],
        },
        grey: { ...gray },
        divider: alpha(gray[500], 0.42),
        background: {
          default: darkBackground,
          paper: darkPaper,
        },
        text: {
          primary: gray[50],
          secondary: gray[300],
          warning: orange[300],
          red: red[300],
          orange: orange[300],
          green: green[300],
          blue: brand[300],
        },
        action: {
          hover: alpha(brand[400], 0.12),
          selected: alpha(brand[400], 0.2),
        },
        baseShadow:
          "hsla(45, 35%, 3%, 0.72) 0px 4px 16px 0px, hsla(45, 30%, 3%, 0.58) 0px 8px 16px -5px",
      },
    },
  };

  const typography = {
    fontFamily,
    h1: {
      fontSize: defaultTheme.typography.pxToRem(48),
      fontWeight: 700,
      lineHeight: 1.15,
      letterSpacing: -0.5,
    },
    h2: {
      fontSize: defaultTheme.typography.pxToRem(36),
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h3: {
      fontSize: defaultTheme.typography.pxToRem(30),
      fontWeight: 600,
      lineHeight: 1.2,
    },
    h4: {
      fontSize: defaultTheme.typography.pxToRem(24),
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: defaultTheme.typography.pxToRem(20),
      fontWeight: 600,
    },
    h6: {
      fontSize: defaultTheme.typography.pxToRem(18),
      fontWeight: 600,
      letterSpacing: 0.15,
    },
    subtitle1: { fontSize: defaultTheme.typography.pxToRem(18) },
    subtitle2: {
      fontSize: defaultTheme.typography.pxToRem(14),
      fontWeight: 600,
    },
    body1: { fontSize: defaultTheme.typography.pxToRem(14) },
    body2: {
      fontSize: defaultTheme.typography.pxToRem(14),
      fontWeight: 400,
    },
    caption: {
      fontSize: defaultTheme.typography.pxToRem(12),
      fontWeight: 400,
    },
    button: {
      fontWeight: 600,
      letterSpacing: 0.2,
    },
  };

  const components = {
    MuiButton: {
      styleOverrides: {
        containedPrimary: ({ theme }) => ({
          boxShadow: "none",
          "&:hover": {
            backgroundColor: brand[700],
            borderColor: brand[800],
            boxShadow: "none",
          },
          ...theme.applyStyles("dark", {
            "&:hover": {
              backgroundColor: brand[500],
              borderColor: brand[600],
              boxShadow: "none",
            },
          }),
        }),
        containedSecondary: ({ theme }) => ({
          boxShadow: "none",
          "&:hover": {
            backgroundColor: gray[700],
            borderColor: gray[800],
            boxShadow: "none",
          },
          ...theme.applyStyles("dark", {
            "&:hover": {
              backgroundColor: gray[500],
              borderColor: gray[600],
              boxShadow: "none",
            },
          }),
        }),
      },
    },
  };

  return {
    brand,
    gray,
    green,
    orange,
    red,
    colorSchemes,
    typography,
    components,
    shape: { borderRadius },
    shadows: [
      "none",
      "var(--template-palette-baseShadow)",
      ...defaultTheme.shadows.slice(2),
    ],
  };
}
