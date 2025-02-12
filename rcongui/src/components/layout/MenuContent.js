import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Stack from "@mui/material/Stack";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import { useNavigate } from "react-router-dom";
import { Collapse } from "@mui/material";
import {useState} from "react";
import { useAppStore } from "@/hooks/useAppState";

const NavigationLink = ({ to, icon, text, onClick }) => {

  return (
    <ListItem key={to} disablePadding sx={{ display: "block" }}>
      <ListItemButton onClick={onClick}>
        {icon && <ListItemIcon>{icon}</ListItemIcon>}
        <ListItemText primary={text} />
      </ListItemButton>
    </ListItem>
  );
};

const Group = ({ groupName, icon, level = 1, children }) => {
  const [open, setOpen] = useState(false);

  const handleClick = () => {
    setOpen(!open);
  };

  return (
    <ListItem key={groupName} disablePadding sx={{ display: "block" }}>
      <ListItemButton onClick={handleClick}>
        {icon && <ListItemIcon>{icon}</ListItemIcon>}
        <ListItemText primary={groupName} />
        {open ? <ExpandLessIcon /> : <ExpandMoreIcon />}
      </ListItemButton>
      <Collapse in={open} timeout={"auto"} unmountOnExit>
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

export default function MenuContent({ navigationTree, isMobile }) {
  const toggleDrawer = useAppStore((state) => state.toggleDrawer);
  const navigate = useNavigate();

  const handleLinkClick = (to) => () => {
    if (isMobile) {
      toggleDrawer();
    }
    navigate(to);
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
        {navigationTree
          .filter((group) => !("name" in group))
          .map((group) =>
            group.links.map((link) => (
              <NavigationLink
                key={link.to}
                to={link.to}
                text={link.name}
                icon={link.icon}
                onClick={handleLinkClick(link.to)}
              />
            ))
          )}

        {navigationTree
          .filter((group) => "name" in group)
          .map((group) => (
            <Group key={group.name} groupName={group.name} icon={group.icon}>
              {group.links.map((link) => (
                <NavigationLink
                  key={link.to}
                  to={link.to}
                  text={link.name}
                  icon={link.icon}
                  onClick={handleLinkClick(link.to)}
                />
              ))}
            </Group>
          ))}
      </List>
    </Stack>
  );
}
