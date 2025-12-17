import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Stack from "@mui/material/Stack";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import { Link } from "react-router-dom";
import { Collapse, TextField, InputAdornment } from "@mui/material";
import {useState} from "react";
import { useAppStore } from "@/stores/app-state";
import SearchIcon from "@mui/icons-material/Search";

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

const Group = ({ groupName, icon, level = 1, children }) => {
  const [open, setOpen] = useState(true);

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
  const [searchTerm, setSearchTerm] = useState("");

  const handleLinkClick = () => {
    if (isMobile) {
      toggleDrawer();
    }
  };

  // Filter navigation tree based on search term
  const filterNavigationTree = (tree, searchTerm) => {
    if (!searchTerm.trim()) {
      return tree;
    }

    const lowerSearchTerm = searchTerm.toLowerCase();

    return tree
      .map((group) => {
        // Check if group has a name (it's a group)
        if ("name" in group) {
          const groupNameMatches = group.name.toLowerCase().includes(lowerSearchTerm);
          
          // Filter links that match
          const matchingLinks = group.links.filter((link) =>
            link.name.toLowerCase().includes(lowerSearchTerm)
          );

          // If group name matches, show all links; if only links match, show group with filtered links
          if (groupNameMatches || matchingLinks.length > 0) {
            return {
              ...group,
              links: groupNameMatches ? group.links : matchingLinks,
            };
          }
          return null;
        } else {
          // It's a link without a group
          const matchingLinks = group.links.filter((link) =>
            link.name.toLowerCase().includes(lowerSearchTerm)
          );

          if (matchingLinks.length > 0) {
            return {
              ...group,
              links: matchingLinks,
            };
          }
          return null;
        }
      })
      .filter((group) => group !== null);
  };

  const filteredTree = filterNavigationTree(navigationTree, searchTerm);

  return (
    <Stack
      sx={{
        flexGrow: 1,
        p: 1,
        overflow: "hidden",
      }}
    >
      <TextField
        size="small"
        placeholder="Search..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ mb: 1 }}
        slotProps={{
          input: {
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }
        }}
      />
      <List dense sx={{ overflowY: "auto" }}>
        {filteredTree
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

        {filteredTree
          .filter((group) => "name" in group)
          .map((group) => (
            <Group key={group.name} groupName={group.name} icon={group.icon}>
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
