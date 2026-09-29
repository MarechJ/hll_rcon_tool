import { alpha } from "@mui/material/styles";
import createMilitaryTheme from "./createMilitaryTheme";

// A deliberately excessive cyber-neon theme. It still exposes the same
// semantic tokens as every other scheme, so errors, warnings and destructive
// actions remain meaningful underneath the visual chaos.
const tokens = createMilitaryTheme({
  brand: {
    50: "#e8ffff",
    100: "#c5ffff",
    200: "#8ffaff",
    300: "#4ef3ff",
    400: "#14ddff",
    500: "#00bce7",
    600: "#0095c2",
    700: "#08779d",
    800: "#0d607f",
    900: "#104f69",
  },
  gray: {
    50: "#fbf9ff",
    100: "#f0ecfa",
    200: "#ddd6ee",
    300: "#bbb1d1",
    400: "#9184ad",
    500: "#716488",
    600: "#584c6d",
    700: "#40364f",
    800: "#241d32",
    900: "#100b1c",
  },
  green: {
    50: "#edffe4",
    100: "#d4ffc4",
    200: "#a5ff8b",
    300: "#6dff4d",
    400: "#39f817",
    500: "#22d409",
    600: "#18aa08",
    700: "#19810d",
    800: "#176611",
    900: "#145313",
  },
  orange: {
    50: "#fffbea",
    100: "#fff3bd",
    200: "#ffe679",
    300: "#ffd22d",
    400: "#ffba00",
    500: "#ef9600",
    600: "#ce6e00",
    700: "#a44904",
    800: "#87380c",
    900: "#732e0f",
  },
  red: {
    50: "#fff0f8",
    100: "#ffe0f0",
    200: "#ffc1e2",
    300: "#ff8bc8",
    400: "#ff45a6",
    500: "#f51b87",
    600: "#d00b68",
    700: "#aa0c53",
    800: "#8d1047",
    900: "#75123e",
  },
  fontFamily: "Montserrat, Roboto, Arial, sans-serif",
  borderRadius: 14,
  lightBackground: "#eeeaff",
  lightPaper: "rgba(255, 255, 255, 0.78)",
  darkBackground: "#07040f",
  darkPaper: "rgba(18, 11, 35, 0.82)",
});

const slopShadowLight =
  "0 12px 40px rgba(87, 34, 255, 0.16), 0 0 24px rgba(0, 221, 255, 0.12)";
const slopShadowDark =
  "0 16px 48px rgba(0, 0, 0, 0.58), 0 0 28px rgba(0, 221, 255, 0.16), 0 0 54px rgba(255, 27, 153, 0.10)";

tokens.colorSchemes.light.palette.secondary = {
  light: "#d899ff",
  main: "#a83cff",
  dark: "#7217c5",
  contrastText: "#ffffff",
};
tokens.colorSchemes.dark.palette.secondary = {
  light: "#ef9dff",
  main: "#d94cff",
  dark: "#9a21bd",
  contrastText: "#100b1c",
};
tokens.colorSchemes.light.palette.divider = alpha("#6335d6", 0.24);
tokens.colorSchemes.dark.palette.divider = alpha("#77ecff", 0.24);
tokens.colorSchemes.light.palette.baseShadow = slopShadowLight;
tokens.colorSchemes.dark.palette.baseShadow = slopShadowDark;

export const components = {
  MuiCssBaseline: {
    styleOverrides: (theme) => ({
      "@keyframes slopperinoDrift": {
        "0%": { backgroundPosition: "0% 20%, 100% 0%, 50% 100%" },
        "50%": { backgroundPosition: "15% 5%, 85% 25%, 35% 80%" },
        "100%": { backgroundPosition: "0% 20%, 100% 0%, 50% 100%" },
      },
      html: { minHeight: "100%" },
      body: {
        minHeight: "100%",
        backgroundColor: "#eeeaff",
        backgroundImage:
          "radial-gradient(circle at 10% 10%, rgba(0, 221, 255, .24), transparent 32%), radial-gradient(circle at 90% 8%, rgba(217, 76, 255, .22), transparent 34%), radial-gradient(circle at 55% 100%, rgba(101, 255, 42, .13), transparent 38%)",
        backgroundAttachment: "fixed",
        backgroundSize: "120% 120%",
        animation: "slopperinoDrift 16s ease-in-out infinite",
        ...theme.applyStyles("dark", {
          backgroundColor: "#07040f",
          backgroundImage:
            "radial-gradient(circle at 8% 12%, rgba(0, 221, 255, .20), transparent 31%), radial-gradient(circle at 92% 6%, rgba(217, 76, 255, .22), transparent 34%), radial-gradient(circle at 55% 105%, rgba(101, 255, 42, .09), transparent 36%)",
        }),
      },
      "#root": { minHeight: "100vh" },
      "*": { scrollbarColor: "#a83cff transparent" },
      "*::-webkit-scrollbar": { width: 10, height: 10 },
      "*::-webkit-scrollbar-track": { background: "transparent" },
      "*::-webkit-scrollbar-thumb": {
        border: "2px solid transparent",
        borderRadius: 99,
        background:
          "linear-gradient(180deg, #14ddff, #a83cff, #f51b87) border-box",
      },
      "*::selection": {
        color: "#100b1c",
        backgroundColor: "#6dff4d",
      },
      "body .MuiCard-root, body .MuiDialog-paper": {
        backdropFilter: "blur(18px) saturate(145%)",
      },
      "body .MuiDialog-root .MuiBackdrop-root": {
        backdropFilter: "blur(10px) saturate(150%)",
        backgroundColor: "rgba(7, 4, 15, 0.62)",
      },
      "body .MuiButton-containedPrimary": {
        backgroundImage:
          "linear-gradient(115deg, #00bce7 0%, #7f42ff 52%, #f51b87 100%)",
        backgroundSize: "180% 180%",
        boxShadow:
          "0 8px 24px rgba(0, 188, 231, .20), 0 0 22px rgba(245, 27, 135, .16)",
        textShadow: "0 1px 8px rgba(255, 255, 255, .35)",
        transition:
          "background-position 220ms ease, box-shadow 220ms ease, transform 120ms ease",
        "&:hover": {
          backgroundPosition: "100% 50%",
          boxShadow:
            "0 10px 30px rgba(0, 188, 231, .30), 0 0 30px rgba(245, 27, 135, .25)",
        },
      },
      "body .MuiOutlinedInput-root.Mui-focused": {
        backgroundImage:
          "linear-gradient(110deg, rgba(20, 221, 255, .06), rgba(217, 76, 255, .08))",
      },
      "body .MuiIconButton-colorPrimary:hover": {
        boxShadow: "0 0 20px rgba(20, 221, 255, .34)",
      },
      "body .MuiButton-contained.Mui-disabled": {
        color: theme.palette.action.disabled,
        backgroundColor: theme.palette.action.disabledBackground,
        backgroundImage: "none",
        borderColor: "transparent",
        boxShadow: "none",
        textShadow: "none",
      },
      "body .MuiButton-outlined.Mui-disabled": {
        color: theme.palette.action.disabled,
        backgroundColor: "transparent",
        backgroundImage: "none",
        borderColor: theme.palette.divider,
        boxShadow: "none",
        textShadow: "none",
      },
      "body .MuiIconButton-root.Mui-disabled": {
        color: theme.palette.action.disabled,
        backgroundColor: "transparent",
        backgroundImage: "none",
        borderColor: theme.palette.divider,
        boxShadow: "none",
      },
      "body .MuiSwitch-root .MuiSwitch-thumb": {
        width: 14,
        height: 14,
        color: "#ffffff",
        backgroundColor: "#ffffff",
        border: "2px solid #40364f",
        boxShadow:
          "0 0 0 1px rgba(255,255,255,.7), 0 0 10px rgba(168,60,255,.35)",
        ...theme.applyStyles("dark", {
          color: "#fbf9ff",
          backgroundColor: "#fbf9ff",
          borderColor: "#100b1c",
          boxShadow:
            "0 0 0 1px rgba(20,221,255,.75), 0 0 12px rgba(20,221,255,.45)",
        }),
      },
      "body .MuiSwitch-switchBase.Mui-disabled .MuiSwitch-thumb": {
        boxShadow: "0 0 0 1px currentColor",
      },
      "body .MuiTabs-indicator": {
        backgroundImage: "linear-gradient(90deg, #14ddff, #d94cff, #f51b87)",
        boxShadow: "0 0 14px rgba(217, 76, 255, .42)",
      },
    }),
  },
  MuiTooltip: {
    styleOverrides: {
      tooltip: {
        border: "1px solid rgba(78, 243, 255, 0.38)",
        background: "linear-gradient(135deg, #15102a 0%, #25113a 100%)",
        boxShadow: "0 0 20px rgba(20, 221, 255, 0.22)",
        color: "#fbf9ff",
        fontWeight: 600,
      },
      arrow: { color: "#25113a" },
    },
  },
  MuiAvatar: {
    styleOverrides: {
      root: {
        border: "1px solid rgba(78, 243, 255, 0.45)",
        boxShadow: "0 0 18px rgba(168, 60, 255, 0.22)",
      },
    },
  },
  MuiBadge: {
    styleOverrides: {
      badge: {
        boxShadow: "0 0 12px currentColor",
        fontWeight: 800,
      },
    },
  },
};

export const {
  brand,
  gray,
  green,
  orange,
  red,
  colorSchemes,
  typography,
  shape,
} = tokens;

export const shadows = [
  "none",
  "var(--template-palette-baseShadow)",
  slopShadowLight,
  slopShadowLight,
  slopShadowDark,
  ...tokens.shadows.slice(5),
];
