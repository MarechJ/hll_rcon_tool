import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Stack from "@mui/material/Stack";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import { Link } from "react-router-dom";
import { Collapse } from "@mui/material";
import { useState } from "react";
import { useAppStore } from "@/stores/app-state";

/**
 * Ein einzelner Navigationslink
 */
const NavigationLink = ({ to, icon, text, onClick }) => {
  return (
    <ListItem key={to} onClick={onClick} disablePadding sx={{ display: "block" }}>
      <ListItemButton component={Link} to={to}>
        {icon && <ListItemIcon>{icon}</ListItemIcon>}
        <ListItemText primary={text} />
      </ListItemButton>
    </ListItem>
  );
};

/**
 * Eine Menügruppe (z. B. "Players", "Maps", "Admin")
 * → jetzt standardmäßig expanded beim Laden
 */
const Group = ({ groupName, icon, level = 1, children }) => {
  const [open, setOpen] = useState(true); // ✅ Menüs starten geöffnet

  const handleClick = () => {
    setOpen(!open); // erlaubt weiterhin manuelles Einklappen
  };

  return (
    <ListItem key={groupName} disablePadding sx={{ display: "block" }}>
      <ListItemButton onClick={handleClick}>
        {icon && <ListItemIcon>{icon}</ListItemIcon>}
        <ListItemText primary={groupName} />
        {open ? <ExpandLessIcon /> : <ExpandMoreIcon />}
      </ListItemButton>

      <Collapse in={open} timeout="auto" unmountOnExit>
        <List
          dense
          sx={{ "& .MuiListItemButton-root": { pl: 2 * level } }}
          disablePadding
        >
          {children}
        </List>
      </Collapse>
    </ListItem>
  );
};

/**
 * Gesamtes Menü (Sidebar-Inhalt)
 */
export default function MenuContent({ navigationTree, isMobile }) {
  const toggleDrawer = useAppStore((state) => state.toggleDrawer);

  const handleLinkClick = () => {
    if (isMobile) {
      toggleDrawer();
    }
  };

  return (
    <Stack
      sx={{
        flexGrow: 1,
        p: 1,
        justifyContent: "space-between",
        overflow: "hidden",
      }}
    >
      <List dense sx={{ overflowY: "auto" }}>
        {/* Links ohne Gruppen-Header */}
        {navigationTree
          .filter((group) => !("name" in group))
          .map((group) =>
            group.links.map((link) => (
              <NavigationLink
                key={link.to}
                to={link.to}
                text={link.name}
                icon={link.icon}
                onClick={handleLinkClick}
              />
            ))
          )}

        {/* Gruppen mit expand/collapse */}
        {navigationTree
          .filter((group) => "name" in group)
          .map((group) => (
            <Group
              key={group.name}
              groupName={group.name}
              icon={group.icon}
            >
              {group.links.map((link) => (
                <NavigationLink
                  key={link.to}
                  to={link.to}
                  text={link.name}
                  icon={link.icon}
                  onClick={handleLinkClick}
                />
              ))}
            </Group>
          ))}
      </List>
    </Stack>
  );
}
