import {
  Box,
  Button,
  Card,
  CardContent,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Menu,
  MenuItem,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { useState } from "react";
import { SYNC_METHODS } from "@/components/Blacklist/BlacklistListCreateDialog";

function serverLabel(blacklist, servers) {
  if (blacklist.servers === null) return "All servers";
  if (blacklist.servers.length === 0) return "No servers";
  if (blacklist.servers.length > 1) return "Multiple servers";
  const serverNumber = blacklist.servers[0];
  return servers[serverNumber] ?? `#${serverNumber}`;
}

export default function BlacklistListPanel({ blacklists, servers, onCreate, onEdit, onDelete }) {
  const [menu, setMenu] = useState(null);

  const closeMenu = () => setMenu(null);

  return (
    <Card sx={{ px: 0.5 }} variant="outlined">
      <CardContent>
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 0.5, px: 1 }}>
          <Typography variant="h6">Blacklist lists</Typography>
          <Button size="small" variant="contained" startIcon={<AddIcon />} onClick={onCreate}>New</Button>
        </Stack>
        <List sx={{ gap: 1 }}>
          {blacklists.map((blacklist) => (
            <ListItem
              key={blacklist.id}
              secondaryAction={
                <Tooltip title="List actions">
                  <span>
                    <IconButton
                      size="large"
                      onClick={(event) => setMenu({ anchor: event.currentTarget, blacklist })}
                      aria-label={`Actions for ${blacklist.name}`}
                      sx={{ p: 0.75, color: "text.secondary" }}
                    >
                      <MoreVertIcon sx={{ fontSize: "1.75rem" }} />
                    </IconButton>
                  </span>
                </Tooltip>
              }
              sx={{
                border: (theme) => `1px solid ${theme.palette.divider}`,
                borderRadius: 1,
                px: 1,
                py: 0.25,
                pr: 5,
                alignItems: "flex-start",
                bgcolor: "background.paper",
              }}
            >
              <ListItemText
                primary={blacklist.name}
                primaryTypographyProps={{
                  sx: {
                    whiteSpace: "normal",
                    overflowWrap: "anywhere",
                    wordBreak: "break-word",
                  },
                }}
                secondary={
                  <Stack gap={0.5} sx={{ mt: 0.25 }}>
                    <Typography
                      variant="caption"
                      noWrap
                      title={serverLabel(blacklist, servers)}
                      sx={{ display: "block", maxWidth: "100%" }}
                    >
                      {serverLabel(blacklist, servers)}
                    </Typography>
                    <Typography variant="caption">{SYNC_METHODS[blacklist.sync] ?? blacklist.sync}</Typography>
                  </Stack>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
      <Menu anchorEl={menu?.anchor} open={Boolean(menu)} onClose={closeMenu}>
        <MenuItem onClick={() => { onEdit(menu.blacklist); closeMenu(); }}>
          <EditIcon color="primary" fontSize="small" sx={{ mr: 1 }} /> Edit
        </MenuItem>
        <MenuItem
          disabled={menu?.blacklist.id === 0}
          onClick={() => { onDelete(menu.blacklist); closeMenu(); }}
        >
          <DeleteIcon color="error" fontSize="small" sx={{ mr: 1 }} /> Delete
        </MenuItem>
      </Menu>
      {blacklists.length === 0 && (
        <Box sx={{ p: 2 }}><Typography color="text.secondary">No blacklist lists found.</Typography></Box>
      )}
    </Card>
  );
}
