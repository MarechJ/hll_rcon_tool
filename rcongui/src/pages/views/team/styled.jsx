import { Box, styled } from "@mui/material";
import { getPlayerTier } from "@/utils/player-utils";

export const TeamContainer = styled(Box)(({ theme }) => ({
  display: "flex",
  gap: theme.spacing(2),
  flexDirection: "row",
  [theme.breakpoints.down("lg")]: {
    flexDirection: "column",
  },
  fontFamily: "Roboto Mono, monospace",
  backgroundColor: theme.palette.background.default,
  padding: theme.spacing(2),
  width: "100%",
  overflow: "hidden",
}));

export const TeamBox = styled(Box)(({ theme }) => ({
  flex: 1,
  borderRadius: theme.shape.borderRadius,
  minWidth: 0,
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
}));

export const ScrollContainer = styled(Box)({
  overflowX: "auto",
  flex: 1,
  display: "flex",
  flexDirection: "column",
});

export const ContentWrapper = styled(Box)({
  minWidth: "min-content",
});

export const gridTemplateColumns = {
  default: "35px minmax(200px, 300px) 60px repeat(6, 60px)",
  sm: "35px minmax(150px, 200px) 60px repeat(6, 60px)",
};

export const SquadHeader = styled(Box)(({ theme, selected }) => ({
  padding: theme.spacing(0.5, 1),
  backgroundColor: theme.palette.background.paper,
  borderBottom: `1px solid ${theme.palette.divider}`,
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  alignItems: "center",
  cursor: "pointer",
  "&:hover": {
    backgroundColor: selected
      ? theme.palette.action.selected
      : theme.palette.action.hover,
  },
  "& .squad-info": {
    gridColumn: "1 / 3",
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
    minWidth: 0,
    "& .squad-name-container": {
      display: "flex",
      alignItems: "center",
      gap: theme.spacing(1),
      minWidth: 0,
      flex: 1,
      "& .MuiTypography-root": {
        color: selected ? theme.palette.primary.main : "inherit",
      },
    },
  },
  "& .squad-stats": {
    display: "contents",
    "& .stat": {
      textAlign: "right",
      fontFamily: "Roboto Mono, monospace",
      whiteSpace: "nowrap",
      fontSize: "0.75rem",
      color: selected
        ? theme.palette.primary.main
        : theme.palette.text.secondary,
    },
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
  },
}));

export const PlayerRow = styled(Box)(({ theme, selected, level }) => ({
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  padding: theme.spacing(0.5, 1),
  alignItems: "center",
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  cursor: "pointer",
  "&:hover": {
    backgroundColor: selected
      ? theme.palette.action.selected
      : theme.palette.action.hover,
  },
  "& .stat": {
    textAlign: "right",
    fontFamily: "Roboto Mono, monospace",
    whiteSpace: "nowrap",
    color: selected ? theme.palette.primary.main : "inherit",
  },
  "& .player-info": {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
    minWidth: 0,
    "& .player-name": {
      overflow: "hidden",
      textOverflow: "ellipsis",
      whiteSpace: "nowrap",
      color: selected ? theme.palette.primary.main : "inherit",
      cursor: "pointer",
      "&:hover": {
        textDecoration: "underline",
      },
    },
  },
  "& .level": {
    fontWeight: "bold",
    textAlign: "center",
    color: selected
      ? theme.palette.primary.main
      : level
      ? tierColors[getPlayerTier(level)]
      : "inherit",
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
    fontSize: "0.875rem",
  },
}));

export const HeaderRow = styled(Box)(({ theme }) => ({
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  padding: theme.spacing(0.5, 1),
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.default,
  position: "sticky",
  top: 0,
  zIndex: 1,
  "& > *": {
    textAlign: "right",
    color: theme.palette.text.secondary,
    fontSize: "0.75rem",
    fontWeight: "bold",
    whiteSpace: "nowrap",
  },
  "& > :nth-of-type(1)": {
    textAlign: "center",
  },
  "& > :nth-of-type(2)": {
    textAlign: "left",
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
    fontSize: "0.75rem",
  },
}));

export const TeamHeaderRow = styled(Box)(({ theme }) => ({
  display: "grid",
  marginBottom: theme.spacing(1),
  gridTemplateColumns: gridTemplateColumns.default,
  padding: theme.spacing(0.5, 1),
  alignItems: "center",
  "& > *": {
    textAlign: "right",
    fontFamily: "Roboto Mono, monospace",
    whiteSpace: "nowrap",
    fontSize: "0.75rem",
    color: theme.palette.text.secondary,
    fontWeight: "bold",
  },
  "& > :nth-of-type(1)": {
    textAlign: "center",
    color: theme.palette.primary.main,
  },
  "& > :nth-of-type(2)": {
    textAlign: "left",
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
  },
}));

export const CommanderRow = styled(Box)(({ theme, selected, level }) => ({
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  padding: theme.spacing(2, 1),
  alignItems: "center",
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  cursor: "pointer",
  "&:hover": {
    backgroundColor: selected
      ? theme.palette.action.selected
      : theme.palette.action.hover,
  },
  "& .stat": {
    textAlign: "right",
    fontFamily: "Roboto Mono, monospace",
    whiteSpace: "nowrap",
    color: selected ? theme.palette.primary.main : "inherit",
  },
  "& .player-info": {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
    minWidth: 0,
    "& .player-name": {
      overflow: "hidden",
      textOverflow: "ellipsis",
      whiteSpace: "nowrap",
      color: selected ? theme.palette.primary.main : "inherit",
      cursor: "pointer",
      "&:hover": {
        textDecoration: "underline",
      },
    },
    "& .no-commander": {
      display: "flex",
      alignItems: "center",
      gap: theme.spacing(1),
      color: selected
        ? theme.palette.primary.contrastText
        : theme.palette.text.secondary,
      fontStyle: "italic",
    },
  },
  "& .level": {
    fontWeight: "bold",
    textAlign: "center",
    color: selected
      ? theme.palette.primary.main
      : level
      ? tierColors[getPlayerTier(level)]
      : "inherit",
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
    fontSize: "0.875rem",
  },
}));
