import Divider from "@mui/material/Divider";
import Drawer, { drawerClasses } from "@mui/material/Drawer";
import Stack from "@mui/material/Stack";
import MenuContent from "./MenuContent";
import SelectContent from "./SelectContent";
import { Box, List, ListItem, ListItemText, IconButton } from "@mui/material";
import { navMenus } from "../Header/nav-data";
import ConnectionStatus from "./sidebar/ConnectionStatus";
import AboutDialog from "./sidebar/About";
import ToggleColorMode from "./ColorModeIconDropdown";
import ColorSchemeSelector from "./ColorSchemeSelector";
import { UserActions } from "./sidebar/UserActions";
import CloseIcon from "@mui/icons-material/Close";

const MobileDrawer = ({ open, toggleDrawer, children }) => {
  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={toggleDrawer}
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        [`& .${drawerClasses.paper}`]: {
          backgroundImage: "none",
          backgroundColor: "background.paper",
          minWidth: 240,
          width: { xs: "100%", sm: "auto" },
        },
      }}
    >
      <Box sx={{ display: "flex", justifyContent: "flex-end", px: 1, pt: 0.5 }}>
        <IconButton size="small" onClick={toggleDrawer}>
          <CloseIcon sx={{ fontSize: 24 }} />
        </IconButton>
      </Box>
      <Stack sx={{ height: "100%", mt: -2 }}>{children}</Stack>
    </Drawer>
  );
};

function AdminSideMenuMobile({ open, toggleDrawer }) {
  return (
    <MobileDrawer open={open} toggleDrawer={toggleDrawer}>
      <MenuContent navigationTree={navMenus} isMobile={true} />
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
      <Stack direction="row" sx={{ gap: 1, px: 1.5, py: 0.5 }}>
        <ColorSchemeSelector />
        <ToggleColorMode />
      </Stack>
      <Divider />
      <Box
        sx={{
          display: "flex",
          p: 1.5,
        }}
      >
        <SelectContent />
      </Box>
      <Divider />
      <UserActions />
    </MobileDrawer>
  );
}

export default AdminSideMenuMobile;
