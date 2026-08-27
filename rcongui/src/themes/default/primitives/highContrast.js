import { alpha, createTheme } from "@mui/material/styles";

const defaultTheme = createTheme();

// High Contrast is an accessibility scheme, not a grayscale novelty theme.
// Semantic hues remain distinct while every foreground/background pairing is
// intentionally separated by a strong luminance difference.
export const brand = {
  50: "#eef6ff",
  100: "#d8ebff",
  200: "#b5d9ff",
  300: "#86c0ff",
  400: "#55a5ff",
  500: "#167fe5",
  600: "#0057b8",
  700: "#003f8f",
  800: "#002d69",
  900: "#001d47",
};

export const gray = {
  50: "#ffffff",
  100: "#f2f2f2",
  200: "#dddddd",
  300: "#c2c2c2",
  400: "#929292",
  500: "#6b6b6b",
  600: "#494949",
  700: "#2d2d2d",
  800: "#151515",
  900: "#000000",
};

export const green = {
  50: "#e9f8ed",
  100: "#c9efd3",
  200: "#99dfa9",
  300: "#72ff9f",
  400: "#22c962",
  500: "#007a35",
  600: "#00622a",
  700: "#004b20",
  800: "#003817",
  900: "#00260f",
};

export const orange = {
  50: "#fff6df",
  100: "#ffe6a3",
  200: "#ffd261",
  300: "#ffcf4a",
  400: "#e99b00",
  500: "#9a5700",
  600: "#814600",
  700: "#683700",
  800: "#4f2900",
  900: "#351b00",
};

export const red = {
  50: "#ffedf0",
  100: "#ffd2da",
  200: "#ffacba",
  300: "#ff8fa3",
  400: "#eb4867",
  500: "#b00020",
  600: "#93001a",
  700: "#760015",
  800: "#590010",
  900: "#3d000b",
};

const lightPalette = {
  common: { black: "#000000", white: "#ffffff" },
  primary: {
    light: brand[500],
    main: brand[700],
    dark: brand[900],
    contrastText: "#ffffff",
  },
  secondary: {
    light: "#7844a8",
    main: "#52227d",
    dark: "#351050",
    contrastText: "#ffffff",
  },
  info: {
    light: brand[500],
    main: brand[700],
    dark: brand[900],
    contrastText: "#ffffff",
  },
  warning: {
    light: orange[400],
    main: orange[600],
    dark: orange[900],
    contrastText: "#ffffff",
  },
  error: {
    light: red[400],
    main: red[500],
    dark: red[800],
    contrastText: "#ffffff",
  },
  success: {
    light: green[400],
    main: green[600],
    dark: green[900],
    contrastText: "#ffffff",
  },
  grey: gray,
  divider: "#000000",
  background: { default: "#ffffff", paper: "#f2f2f2" },
  text: {
    primary: "#000000",
    secondary: "#2d2d2d",
    disabled: "#494949",
    warning: orange[700],
    red: red[700],
    orange: orange[700],
    green: green[700],
    blue: brand[800],
  },
  action: {
    active: "#000000",
    hover: alpha("#000000", 0.12),
    selected: alpha("#003f8f", 0.18),
    disabled: "#494949",
    disabledBackground: "#dddddd",
    focus: alpha("#003f8f", 0.25),
  },
  baseShadow: "0 0 0 1px #000000, 0 5px 16px rgba(0,0,0,.22)",
};

const darkPalette = {
  common: { black: "#000000", white: "#ffffff" },
  primary: {
    light: brand[200],
    main: brand[300],
    dark: brand[500],
    contrastText: "#000000",
  },
  secondary: {
    light: "#f0c4ff",
    main: "#dfa0ff",
    dark: "#b869e0",
    contrastText: "#000000",
  },
  info: {
    light: "#b9f3ff",
    main: "#71e5ff",
    dark: "#2cb9d4",
    contrastText: "#000000",
  },
  warning: {
    light: "#ffe79a",
    main: "#ffcf4a",
    dark: "#d69b00",
    contrastText: "#000000",
  },
  error: {
    light: "#ffc0cb",
    main: red[300],
    dark: red[400],
    contrastText: "#000000",
  },
  success: {
    light: "#bdffcf",
    main: green[300],
    dark: green[400],
    contrastText: "#000000",
  },
  grey: gray,
  divider: "#ffffff",
  background: { default: "#000000", paper: "#151515" },
  text: {
    primary: "#ffffff",
    secondary: "#f2f2f2",
    disabled: "#c2c2c2",
    warning: "#ffcf4a",
    red: "#ff8fa3",
    orange: "#ffcf4a",
    green: "#72ff9f",
    blue: "#86c0ff",
  },
  action: {
    active: "#ffffff",
    hover: alpha("#ffffff", 0.16),
    selected: alpha("#86c0ff", 0.24),
    disabled: "#c2c2c2",
    disabledBackground: "#2d2d2d",
    focus: alpha("#86c0ff", 0.34),
  },
  baseShadow: "0 0 0 1px #ffffff, 0 6px 20px rgba(255,255,255,.14)",
};

export const colorSchemes = {
  light: { palette: lightPalette },
  dark: { palette: darkPalette },
};

export const typography = {
  fontFamily: "Montserrat, Roboto, Arial, sans-serif",
  h1: {
    fontSize: defaultTheme.typography.pxToRem(48),
    fontWeight: 700,
    lineHeight: 1.15,
  },
  h2: {
    fontSize: defaultTheme.typography.pxToRem(36),
    fontWeight: 700,
    lineHeight: 1.2,
  },
  h3: {
    fontSize: defaultTheme.typography.pxToRem(30),
    fontWeight: 700,
    lineHeight: 1.2,
  },
  h4: {
    fontSize: defaultTheme.typography.pxToRem(24),
    fontWeight: 700,
    lineHeight: 1.35,
  },
  h5: { fontSize: defaultTheme.typography.pxToRem(20), fontWeight: 700 },
  h6: { fontSize: defaultTheme.typography.pxToRem(18), fontWeight: 700 },
  subtitle1: { fontSize: defaultTheme.typography.pxToRem(18), fontWeight: 600 },
  subtitle2: { fontSize: defaultTheme.typography.pxToRem(14), fontWeight: 700 },
  body1: { fontSize: defaultTheme.typography.pxToRem(16), lineHeight: 1.65 },
  body2: { fontSize: defaultTheme.typography.pxToRem(16), lineHeight: 1.65 },
  caption: { fontSize: defaultTheme.typography.pxToRem(13), fontWeight: 500 },
  button: { fontWeight: 700, letterSpacing: 0.2 },
};

export const shape = { borderRadius: 2 };

export const shadows = [
  "none",
  "var(--template-palette-baseShadow)",
  ...defaultTheme.shadows.slice(2),
];

export const components = {
  MuiCssBaseline: {
    styleOverrides: (theme) => ({
      "body :focus-visible": {
        outline: `3px solid ${theme.palette.primary.main}`,
        outlineOffset: 3,
      },
      "body .Mui-disabled": { opacity: 1 },
      "body .MuiButton-root.Mui-disabled, body .MuiIconButton-root.Mui-disabled":
        {
          color: theme.palette.action.disabled,
          backgroundColor: theme.palette.action.disabledBackground,
          border: `1px dashed ${theme.palette.text.primary}`,
        },
      "body .MuiInputBase-root.Mui-disabled": {
        color: theme.palette.text.disabled,
        WebkitTextFillColor: theme.palette.text.disabled,
      },
      "body a": { textDecorationThickness: "2px" },
      "@media (prefers-reduced-motion: reduce)": {
        "*, *::before, *::after": {
          scrollBehavior: "auto !important",
          transitionDuration: "0.01ms !important",
          animationDuration: "0.01ms !important",
          animationIterationCount: "1 !important",
        },
      },
    }),
  },
};
