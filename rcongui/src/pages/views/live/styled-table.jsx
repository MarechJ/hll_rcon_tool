import { styled } from "@mui/material";

// The table will have a prop size ["small", "default", "large"]
// Styles will be different based on the size property
// The property size won't be passed to the component, but rather it will be used in the styled component
export const StyledTable = styled("table", {
  shouldForwardProp: (prop) => prop !== "size",
})((styledProps) => {
  const theme = styledProps.theme;
  const size = styledProps.size ?? "medium";
  return {
    fontSize: size === "small" ? 12 : size === "large" ? 18 : 14,
    borderCollapse: "collapse",
    borderSpacing: 0,
    border: `1px solid ${theme.palette.divider}`,
  };
});

export const StyledTh = styled("th", {
  shouldForwardProp: (prop) => prop !== "size",
})((styledProps) => {
  const size = styledProps.size;
  return {
    padding: "1px 4px",
    textAlign: "left",
    minWidth:
      size === "icon"
        ? 30
        : size === "medium"
        ? 100
        : size === "large"
        ? 200
        : size === "full"
        ? "100%"
        : "auto",
  };
});

export const StyledTd = styled("td")(({ theme }) => ({
  padding: "1px 4px",
}));

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
