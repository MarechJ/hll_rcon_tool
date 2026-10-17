import { Box, Tab, Tabs } from "@mui/material";
import { Link, useLocation } from "react-router-dom";

const VipManagementTabs = () => {
  const { pathname } = useLocation();

  return (
    <Box component="nav" aria-label="VIP management sections" sx={{ borderBottom: 1, borderColor: "divider" }}>
      <Tabs value={pathname === "/records/vips" ? "gameserver" : "lists"}>
        <Tab label="VIP Lists" value="lists" component={Link} to="/records/vip-lists" />
        <Tab label="Gameserver Status" value="gameserver" component={Link} to="/records/vips" />
      </Tabs>
    </Box>
  );
};

export default VipManagementTabs;
