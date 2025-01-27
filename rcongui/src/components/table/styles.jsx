import { Button, styled } from "@mui/material";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";

export function getVariantWidth(variant) {
  switch (variant) {
    case "icon":
      return "1.5rem";
    case "short":
      return "4rem";
    case "time":
      return "16ch";
    case "name":
      return "20ch";
    case "fullname":
      return "30ch";
    case "action":
      return "24ch";
    case "content":
      return "auto";
    default:
      return "auto";
  }
}

export function getVariantMinWidth(variant) {
  switch (variant) {
    case "icon":
      return "1.5rem";
    case "short":
      return "4rem";
    case "time":
      return "16ch";
    case "name":
      return "20ch";
    case "fullname":
      return "30ch";
    case "action":
      return "24ch";
    case "content":
      return "50ch";
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
        paddingRight: theme.spacing(1.25),
        paddingLeft: theme.spacing(1.25),
        paddingTop: theme.spacing(1.25),
        paddingBottom: theme.spacing(1.25),
      };
    default:
      return {
        paddingRight: theme.spacing(1),
        paddingLeft: theme.spacing(1),
        paddingTop: theme.spacing(1),
        paddingBottom: theme.spacing(1),
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
        ? theme.typography.pxToRem(12)
        : fontSize === "large"
        ? theme.typography.pxToRem(20)
        : theme.typography.pxToRem(16),
    borderCollapse: "collapse",
    borderSpacing: 0,
    border: `1px solid ${theme.palette.divider}`,
    width: "100%",
    "& td": {
      ...getDensityPadding(density, theme),
    },
    "& th": {
      ...getDensityPadding(density, theme),
      paddingTop: "unset",
      paddingBottom: "unset",
    },
    "& tbody tr": {
      verticalAlign: "top",
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

export const SortableHeader =
  (text) =>
  ({ column }) => {
    return (
      <HeaderButton onClick={column.getToggleSortingHandler()}>
        {text}
        {column.getIsSorted() &&
          (column.getIsSorted() === "asc" ? (
            <ArrowUpwardIcon
              sx={{
                fontSize: "1em",
                width: "1em",
                height: "1em",
                ml: 0.5,
              }}
            />
          ) : (
            <ArrowDownwardIcon
              sx={{
                fontSize: "1em",
                width: "1em",
                height: "1em",
                ml: 0.5,
              }}
            />
          ))}
      </HeaderButton>
    );
  };
