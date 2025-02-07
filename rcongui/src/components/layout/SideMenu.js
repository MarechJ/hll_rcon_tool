import { styled } from "@mui/material/styles";
import Avatar from "@mui/material/Avatar";
import MuiDrawer, { drawerClasses } from "@mui/material/Drawer";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import SelectContent from "./SelectContent";
import MenuContent from "./MenuContent";
import OptionsMenu from "./OptionsMenu";
import { useAuth } from "@/hooks/useAuth";
import { navMenus } from "../Header/nav-data";
import { List, ListItem, ListItemText } from "@mui/material";
import ConnectionStatus from "./sidebar/ConnectionStatus";
import AboutDialog from "./sidebar/About";
import ServerStatus from "../Header/server-status";
import { useAppStore } from "@/hooks/useAppState";
import { UserActions } from "./sidebar/UserActions";

const drawerWidth = 240;

const Drawer = styled(MuiDrawer, {
  shouldForwardProp: (prop) => prop !== "open",
})(({ open }) => ({
  width: drawerWidth,
  flexShrink: 0,
  boxSizing: "border-box",
  mt: 10,
  [`& .${drawerClasses.paper}`]: {
    width: drawerWidth,
    boxSizing: "border-box",
    ...(!open && {
      width: 0,
    }),
  },
}));

export const MenuDrawer = ({ open, children }) => {
  return (
    <Drawer
      variant="permanent"
      open={open}
      sx={{
        width: open ? drawerWidth : 0,
        display: { xs: "none", lg: "block" },
        [`& .${drawerClasses.paper}`]: {
          backgroundColor: "background.paper",
        },
      }}
    >
      {children}
    </Drawer>
  );
};

export default function SideMenu() {
  const openDrawer = useAppStore((state) => state.openDrawer);

  return (
    <MenuDrawer open={openDrawer}>
      <ServerStatus />
      <Divider />
      <MenuContent navigationTree={navMenus} />
      <List dense>
        <ListItem>
          <ListItemText
            sx={{ marginLeft: -0.5 }}
            primary={<ConnectionStatus />}
          />
        </ListItem>
        <AboutDialog />
      </List>
      <Divider />
      <Box
        sx={{
          display: "flex",
          p: 1.5,
        }}
      >
        <SelectContent />
      </Box>
      <UserActions />
    </MenuDrawer>
  );
}
