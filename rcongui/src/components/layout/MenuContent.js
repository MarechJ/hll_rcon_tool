import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Stack from "@mui/material/Stack";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import { Link } from "react-router-dom";
import { Collapse, TextField, InputAdornment, IconButton, Box } from "@mui/material";
import { useEffect, useMemo, useRef, useState } from "react";
import { useAppStore } from "@/stores/app-state";
import SearchIcon from "@mui/icons-material/Search";
import CloseIcon from "@mui/icons-material/Close";

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

const Group = ({ groupName, icon, level = 1, open, forceOpen = false, onToggle, children }) => {
  const isOpen = forceOpen || open;

  return (
    <ListItem key={groupName} disablePadding sx={{ display: "block" }}>
      <ListItemButton onClick={onToggle}>
        {icon && <ListItemIcon>{icon}</ListItemIcon>}
        <ListItemText primary={groupName} />
        {isOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
      </ListItemButton>
      <Collapse in={isOpen} timeout={"auto"} unmountOnExit>
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
  const groupOpenState = useAppStore((state) => state.groupOpenState);
  const toggleMenuGroupOpen = useAppStore((state) => state.toggleMenuGroupOpen);
  const [searchTerm, setSearchTerm] = useState("");
  const searchInputRef = useRef(null);

  const isApplePlatform = useMemo(() => {
    if (typeof navigator === "undefined") return false;
    const ua = navigator.userAgent || "";
    const uaPlatform = navigator.userAgentData?.platform || "";
    return /mac|iphone|ipad|ipod/i.test(uaPlatform) || /Mac OS X|Macintosh|iPhone|iPad|iPod/i.test(ua);
  }, []);

  const keyHintLabel = isApplePlatform ? "⌘K" : "Ctrl+K";

  useEffect(() => {
    const onKeyDown = (e) => {
      const key = (e.key || "").toLowerCase();
      if (key !== "k") return;

      const comboPressed = isApplePlatform ? e.metaKey : e.ctrlKey;
      if (!comboPressed) return;

      e.preventDefault();
      e.stopPropagation();

      const el = searchInputRef.current;
      if (!el) return;
      el.focus();
      if (typeof el.select === "function") el.select();
    };

    window.addEventListener("keydown", onKeyDown, { capture: true });
    return () => window.removeEventListener("keydown", onKeyDown, { capture: true });
  }, [isApplePlatform]);

  const toggleGroup = (groupName) => {
    toggleMenuGroupOpen(groupName);
  };

  const isGroupOpen = (groupName) => !!groupOpenState[groupName];

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
      <Stack direction={"row"} alignItems={"start"} spacing={0.5}>
        <TextField
          size="small"
          fullWidth
          placeholder="Search..."
          name="crcon-search"
          inputRef={searchInputRef}
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
              endAdornment: (
                <InputAdornment position="end">
                  <Box
                    aria-hidden
                    onMouseDown={(e) => {
                      // Keep focus in the input when clicking the hint.
                      e.preventDefault();
                      searchInputRef.current?.focus?.();
                    }}
                    sx={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 0.75,
                      px: 0.75,
                      py: 0.25,
                      borderRadius: 1,
                      border: "1px solid",
                      borderColor: "divider",
                      bgcolor: (theme) => theme.palette.background.paper,
                      color: "text.secondary",
                      fontSize: 12,
                      lineHeight: 1,
                      fontFamily:
                        'ui-monospace, SFMono-Regular, SF Mono, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                      letterSpacing: 0.2,
                      userSelect: "none",
                      boxShadow: (theme) =>
                        `inset 0 1px 0 ${theme.palette.action.hover}, inset 0 -1px 0 ${theme.palette.action.selected}`,
                    }}
                  >
                    {keyHintLabel}
                  </Box>
                </InputAdornment>
              ),
            }
          }}
        />
        {isMobile && (
          <IconButton size="small" onClick={toggleDrawer}>
            <CloseIcon sx={{ fontSize: 24 }} />
          </IconButton>
        )}
      </Stack>
      <List dense sx={{ overflowY: "auto", scrollbarWidth: "none" }}>
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
            <Group
              key={group.name}
              groupName={group.name}
              icon={group.icon}
              open={isGroupOpen(group.name)}
              forceOpen={!!searchTerm.trim()}
              onToggle={() => toggleGroup(group.name)}
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
