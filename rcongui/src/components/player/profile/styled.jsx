import { Badge, Box, Drawer, Stack, styled } from "@mui/material";
import { green, red } from "@mui/material/colors";

export const OnlineStatusBadge = styled(Badge, {
  shouldForwardProp: (props) => props !== "isOnline",
})(({ theme, isOnline }) => ({
  "& .MuiBadge-badge": {
    backgroundColor: isOnline ? green["500"] : red["500"],
    color: isOnline ? green["500"] : red["500"],
    boxShadow: `0 0 0 2px ${theme.palette.background.paper}`,
    "&::after": {
      position: "absolute",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
      borderRadius: "50%",
      animation: isOnline ? "ripple 1.2s infinite ease-in-out" : "none",
      border: "1px solid currentColor",
      content: '""',
    },
  },
  "@keyframes ripple": {
    "0%": {
      transform: "scale(.8)",
      opacity: 1,
    },
    "100%": {
      transform: "scale(2.4)",
      opacity: 0,
    },
  },
}));

export const ResponsiveDrawer = styled(Drawer)(({ theme }) => ({
  "& .MuiDrawer-paper": {
    width: "100%",
    [theme.breakpoints.up("sm")]: {
      width: "30rem",
    },
  },
}));

export const ProfileWrapper = styled(Box)(({ theme }) => ({
  width: "100%",
  height: "100%",
  overflowX: "hidden",
  paddingTop: theme.spacing(1),
  paddingBottom: theme.spacing(2),
  [theme.breakpoints.up("sm")]: {
    width: "30rem",
  },
}));

export const ProfileHeader = styled(Stack)(({ theme }) => ({
  paddingRight: theme.spacing(1),
  paddingLeft: theme.spacing(2),
  paddingTop: theme.spacing(2),
  marginBottom: theme.spacing(1),
  alignItems: "center",
  textAlign: "center",
  position: "relative",
}));

export const Message = styled(Box)(({ theme }) => ({
  background:
    theme.palette.mode === "dark"
      ? theme.palette.primary.dark
      : theme.palette.primary.light,
  color: theme.palette.primary.contrastText,
  paddingTop: theme.spacing(1),
  paddingBottom: theme.spacing(1),
  paddingRight: theme.spacing(1.5),
  paddingLeft: theme.spacing(1.5),
  borderRadius: theme.shape.borderRadius,
  borderBottomRightRadius: 0,
}));
