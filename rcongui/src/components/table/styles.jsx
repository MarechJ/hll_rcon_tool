import { Button, styled } from "@mui/material";

export function getVariantWidth(variant) {
  switch (variant) {
    case "icon":
      return "1.25em";
    case "short":
      return "4em";
    case "time":
      return "16ch";
    case "name":
      return "20ch";
    case "fullname":
      return "30ch";
    case "action":
      return "24ch";
    case "content":
      return "auto"
    default:
      return "auto";
  }
}

export function getVariantMinWidth(variant) {
  switch (variant) {
    case "icon":
      return "1.25em";
    case "short":
      return "4em";
    case "time":
      return "16ch";
    case "name":
      return "20ch";
    case "fullname":
      return "30ch";
    case "action":
      return "24ch";
    case "content":
      return "50ch"
    default:
      return "auto";
  }
}

export function getDensityPadding(density, theme) {
  switch (density) {
    case "dense":
      return {
        paddingRight: theme.spacing(0.25),
        paddingLeft: theme.spacing(0.25),
        paddingTop: theme.spacing(0.25),
        paddingBottom: theme.spacing(0.25),
      };
    case "comfortable":
      return {
        paddingRight: theme.spacing(1),
        paddingLeft: theme.spacing(1),
        paddingTop: theme.spacing(1),
        paddingBottom: theme.spacing(1),
      };
    default:
      return {
        paddingRight: theme.spacing(0.5),
        paddingLeft: theme.spacing(0.5),
        paddingTop: theme.spacing(0.5),
        paddingBottom: theme.spacing(0.5),
      };
  }
}

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
        ? "0.85rem"
        : fontSize === "large"
        ? "1.15rem"
        : "1rem",
    borderCollapse: "collapse",
    borderSpacing: 0,
    border: `1px solid ${theme.palette.divider}`,
    width: "100%",
    "& td": {
      ...getDensityPadding(density, theme),
      verticalAlign: "middle",
    },
    "& th": {
      ...getDensityPadding(density, theme),
      verticalAlign: "middle",
    },
  };
});

export const StyledTh = styled("th", {
  shouldForwardProp: (prop) => prop !== "variant" || prop !== "minWidth",
})((styledProps) => {
  const variant = styledProps.variant;
  return {
    width: getVariantWidth(variant),
    minWidth: getVariantMinWidth(variant),
    textAlign: variant === "icon" ? "center" : "left",
  };
});

export const StyledTd = styled("td", {
  shouldForwardProp: (prop) => prop !== "variant" || prop !== "minWidth",
})((styledProps) => {
  const variant = styledProps.variant;

  return {
    width: getVariantWidth(variant),
    minWidth: getVariantMinWidth(variant),
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

export const Action = styled("div", {
  shouldForwardProp: (props) => props !== "type",
})(({ theme, type }) => ({
  "&::before": {
    content: `"${actionToEmoji[type] ?? actionToEmoji["UNKNOWN"]}"`,
    paddingRight: theme.spacing(1),
  },
  textAlign: "left",
}));

export const TextButton = styled((props) => (
  <span role="button" tabIndex={0} {...props} />
))(({ theme }) => ({
  cursor: "pointer",
  width: "fit-content",
  "&:hover": {
    textDecoration: "underline",
  },
}));

export const HeaderButton = styled((props) => (
  <Button size="small" {...props} />
))(({ theme }) => ({
  width: "100%",
  borderRadius: 0,
  textAlign: "left",
  color: theme.palette.text.primary,
  fontSize: "1em",
  textDecoration: "none",
  textTransform: "none",
}));

export const SortableHeader =
  (text) =>
  ({ column }) => {
    return (
      <HeaderButton onClick={column.getToggleSortingHandler()}>
        {text}
      </HeaderButton>
    );
  };
