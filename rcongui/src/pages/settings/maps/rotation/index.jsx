import { Box, Tabs } from "@mui/material";
import { Outlet, useLocation } from "react-router-dom";
import { NavLinkTab } from "@/components/shared/NavLinkTab";

/**
 * Map Rotation page that contains the map rotation builder component
 */
function MapRotation() {
  // Get active tab
  const location = useLocation();
  const tabs = [
    { label: "Builder", href: "/settings/maps/rotation" },
    { label: "Settings", href: "/settings/maps/rotation/settings" },
  ];
  const activeTab = tabs.findIndex(({ href }) =>
    location.pathname.endsWith(href)
  );

  return (
    <>
      <Tabs value={activeTab}>
        <NavLinkTab label={"Builder"} to={""} />
        <NavLinkTab label={"Settings"} to={"settings"} />
      </Tabs>
      {/* Move to Outlet */}
      <Box sx={{ mt: 1 }}>
        <Outlet />
      </Box>
    </>
  );
}

export default MapRotation;
