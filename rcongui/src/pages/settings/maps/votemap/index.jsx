import { Box, Tabs } from "@mui/material";
import { Outlet, useLocation } from "react-router-dom";
import { NavLinkTab } from "@/components/shared/NavLinkTab";

/**
 * Map Rotation page that contains the map rotation builder component
 */
function VotemapPage() {
  // Get active tab
  const location = useLocation();
  const tabs = [
    { label: "Status", href: "/settings/maps/votemap" },
    { label: "Map Whitelist", href: "/settings/maps/votemap/builder" },
    { label: "Settings", href: "/settings/maps/votemap/settings" },
  ];
  const activeTab = tabs.findIndex(({ href }) =>
    location.pathname.endsWith(href)
  );

  return (
    <>
      <Tabs value={activeTab}>
        {tabs.map(({ href, label }) => (
          <NavLinkTab key={href} label={label} to={href} />
        ))}
      </Tabs>
      {/* Move to Outlet */}
      <Box sx={{ mt: 1 }}>
        <Outlet />
      </Box>
    </>
  );
}

export default VotemapPage;
