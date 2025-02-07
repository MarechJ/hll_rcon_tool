import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Drawer, { drawerClasses } from "@mui/material/Drawer";
import Stack from "@mui/material/Stack";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import MenuContent from "./MenuContent";
import SelectContent from "./SelectContent";
import { Box, List, ListItem, ListItemText } from "@mui/material";
import { Form } from "react-router-dom";
import { navMenus } from "../Header/nav-data";
import ConnectionStatus from "./sidebar/ConnectionStatus";
import AboutDialog from "./sidebar/About";

import ToggleWidthMode from "./ToggleWidthMode";
import ToggleColorMode from "./ColorModeIconDropdown";
import ColorSchemeSelector from "./ColorSchemeSelector";
import { UserActions } from "./sidebar/UserActions";

const MobileDrawer = ({ open, toggleDrawer, children }) => {
  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={toggleDrawer(false)}
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        [`& .${drawerClasses.paper}`]: {
          backgroundImage: "none",
          backgroundColor: "background.paper",
          minWidth: 240,
        },
      }}
    >
      <Stack
        sx={{
          maxWidth: "70dvw",
          height: "100%",
        }}
      >
        {children}
      </Stack>
    </Drawer>
  );
};

function AdminSideMenuMobile({ open, toggleDrawer }) {
  return (
    <MobileDrawer open={open} toggleDrawer={toggleDrawer}>
      <Stack sx={{ flexGrow: 1 }}>
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
      </Stack>
      <UserActions />
    </MobileDrawer>
  );
}

export default AdminSideMenuMobile;
