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
import NewReleases from "./NewReleases";
import ConnectionStatus from "./ConnectionStatus";

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
      <Box sx={{ mt: "60px" }}></Box>
      {children}
    </Drawer>
  );
};

export default function SideMenu({ open }) {
  const { permissions } = useAuth();

  return (
    <MenuDrawer open={open}>
      <MenuContent navigationTree={navMenus} />
      <List dense>
        <ListItem>
          <ListItemText sx={{ marginLeft: -0.5 }} primary={<ConnectionStatus />} />
        </ListItem>
        <NewReleases />
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
      <Stack
        direction="row"
        sx={{
          p: 2,
          gap: 1,
          alignItems: "center",
          borderTop: "1px solid",
          borderColor: "divider",
        }}
      >
        <Avatar
          sizes="small"
          alt={permissions?.user_name?.toUpperCase() ?? "?"}
          src="/static/images/avatar/7.jpg"
          sx={{ width: 36, height: 36 }}
        />
        <Box sx={{ mr: "auto" }}>
          <Typography
            variant="body2"
            sx={{ fontWeight: 500, lineHeight: "16px" }}
          >
            {permissions.user_name ?? "?????"}
          </Typography>
        </Box>
        <OptionsMenu />
      </Stack>
    </MenuDrawer>
  );
}
