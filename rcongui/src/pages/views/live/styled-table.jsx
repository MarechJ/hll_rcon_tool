import { Button, styled } from "@mui/material";

// The table will have a prop size ["small", "normal", "large"]
// Styles will be different based on the size property
// The property size won't be passed to the component, but rather it will be used in the styled component
export const StyledTable = styled("table", {
  shouldForwardProp: (prop) => prop !== "fontSize" || prop !== "density",
})((styledProps) => {
  const theme = styledProps.theme;
  const fontSize = styledProps.fontSize;
  const density = styledProps.density;

  return {
    // TABLE
    fontSize:
      fontSize === "small"
        ? theme.typography.pxToRem(12)
        : fontSize === "large"
        ? theme.typography.pxToRem(20)
        : theme.typography.pxToRem(16),
    borderCollapse: "collapse",
    borderSpacing: 0,
    border: `1px solid ${theme.palette.divider}`,
    width: "100%",
    "& td": {
      paddingRight: density === "small" ? 2 : density === "large" ? 6 : 4,
      paddingLeft: density === "small" ? 2 : density === "large" ? 6 : 4,
      paddingTop:
        density === "small"
          ? theme.spacing(0.25)
          : density === "large"
          ? theme.spacing(1.25)
          : theme.spacing(0.75),
      paddingBottom:
        density === "small"
          ? theme.spacing(0.25)
          : density === "large"
          ? theme.spacing(1.25)
          : theme.spacing(0.75),
    },
    "& th": {
      paddingRight: density === "small" ? 2 : density === "large" ? 6 : 4,
      paddingLeft: density === "small" ? 2 : density === "large" ? 6 : 4,
    },
  };
});

export const StyledTh = styled("th", {
  shouldForwardProp: (prop) => prop !== "variant",
})((styledProps) => {
  const variant = styledProps.variant;
  return {
    padding: variant === "short" ? "4px" : "1px 4px",
    width: variant === "icon" ? "1.5rem" : variant === "short" ? "4rem" : "auto",
    textAlign: variant === "icon" ? "center" : "left",
  };
});

export const StyledTd = styled("td", {
  shouldForwardProp: (prop) => prop !== "variant",
})((styledProps) => {
  const theme = styledProps.theme;
  const variant = styledProps.variant;

  return {
    width: variant === "icon" ? "1.5rem" : variant === "short" ? "4rem" : "auto",
    textAlign: variant === "icon" ? "center" : "left",
  };
});

export const StyledTr = styled("tr")(({ theme }) => ({
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const actionToEmoji = {
  ADMIN: "🚨",
  "ADMIN MISC": "🚨",
  "ADMIN IDLE": "💤",
  "ADMIN ANTI-CHEAT": "🚷",
  "ADMIN BANNED": "⌛",
  "ADMIN PERMA BANNED": "⛔",
  "ADMIN KICKED": "🚷",
  CHAT: "💬",
  CAMERA: "👀",
  "CHAT[Allies]": "🟦",
  "CHAT[Allies][Team]": "🟦",
  "CHAT[Allies][Unit]": "🟦",
  "CHAT[Axis]": "🟥",
  "CHAT[Axis][Team]": "🟥",
  "CHAT[Axis][Unit]": "🟥",
  CONNECTED: "🛬",
  DISCONNECTED: "🛫",
  KILL: "💀",
  MATCH: "🏁",
  "MATCH ENDED": "🏁",
  "MATCH START": "🏁",
  MESSAGE: "📢",
  "TEAM KILL": "⚠️",
  TEAMSWITCH: "♻️",
  "TK AUTO": "🚷",
  "TK AUTO BANNED": "⌛",
  "TK AUTO KICKED": "🚷",
  VOTE: "🙋",
  "VOTE COMPLETED": "🙋",
  "VOTE EXPIRED": "🙋",
  "VOTE PASSED": "🙋",
  "VOTE STARTED": "🙋",
  UNKNOWN: "❓",
};

export const Action = styled("span", {
  shouldForwardProp: (props) => props !== "type",
})(({ theme, type }) => ({
  display: "inline-block",
  "&::before": {
    content: `"${actionToEmoji[type] ?? actionToEmoji["UNKNOWN"]}"`,
    display: "inline-block",
    paddingRight: theme.spacing(1),
  },
}));

export const TextButton = styled((props) => (
  <span role="button" tabIndex={0} {...props} />
))(({ theme }) => ({
  cursor: "pointer",
  "&:hover": {
    textDecoration: "underline",
  },
}));

export const HeaderButton = styled((props) => (
  <Button size="small" {...props} />
))(({ theme }) => ({
  width: "100%",
  minWidth: 16,
  minHeight: 16,
  p: 0,
  borderRadius: 0,
  textAlign: "left",
  color: theme.palette.text.primary,
  fontSize: "inherit",
  textDecoration: "none",
  textTransform: "none",
}));
