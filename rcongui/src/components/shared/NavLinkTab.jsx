// A component that renders a tab with a link to a page
// It is used in the Tabs component to create a tab that links to a page

import { Tab } from "@mui/material";
import { Link } from "react-router-dom";

export function NavLinkTab({ label, to, ...props }) {
  return (
    <Tab
      component={Link}
      to={to}
      label={label}
      {...props}
    />
  );
}