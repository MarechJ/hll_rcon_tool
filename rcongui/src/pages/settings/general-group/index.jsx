import { NavLinkTab } from "@/components/shared/NavLinkTab";
import { Alert, Box, Tabs } from "@mui/material";
import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";

function SettingsPage() {
  const [showAlert, setShowAlert] = useState(true);
  // Get active tab
  const location = useLocation();
  const tabs = [
    { label: "General", href: "/settings/general" },
    { label: "Game", href: "/settings/game" },
    { label: "Server Name", href: "/settings/server-name" },
    { label: "Admin Cam", href: "/settings/admin-cam-notifications" },
    { label: "CRCON APP", href: "/settings/crcon" },
  ];
  const activeTab = tabs.findIndex(({ href }) =>
    location.pathname.endsWith(href)
  );

  return (
    <>
      <Tabs
        value={activeTab}
        variant="scrollable"
        scrollButtons="auto"
        allowScrollButtonsMobile
      >
        {tabs.map(({ href, label }) => (
          <NavLinkTab key={href} label={label} to={href} />
        ))}
      </Tabs>
      <Box sx={{ mt: 1 }}>
        {showAlert && (
          <Alert
            severity="info"
            onClose={() => setShowAlert(false)}
            sx={{ mb: 4 }}
          >
            Displayed values may not match the current server settings, as the
            HLL server doesn't provide this data as of version U18. You can
            still adjust settings. This will be fixed in a future update.
          </Alert>
        )}
        <Outlet />
      </Box>
    </>
  );
}

export default SettingsPage;
