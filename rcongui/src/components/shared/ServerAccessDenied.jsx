import { Box, Button, Card, CardContent, List, ListItem, ListItemButton, ListItemText, Stack, Typography, Alert, AlertTitle } from "@mui/material";
import LockIcon from "@mui/icons-material/Lock";
import ServerIcon from "@mui/icons-material/Dns";
import { useGlobalStore } from "@/stores/global-state";

export default function ServerAccessDenied({ errorMessage }) {
  const serverState = useGlobalStore((state) => state.serverState);
  const servers = useGlobalStore((state) => state.servers);

  const availableServers = [serverState, ...servers].filter(Boolean);

  const handleServerClick = (server) => {
    if (!server.link) {
      console.error("Server has no link:", server);
      return;
    }

    const url = new URL(server.link);
    url.pathname = window.location.pathname;
    url.search = window.location.search;
    
    window.location.href = url.toString();
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        backgroundColor: (theme) => theme.palette.background.default,
        padding: 3,
      }}
    >
      <Stack spacing={3} sx={{ maxWidth: 600, width: "100%" }}>
        <Alert severity="error" icon={<LockIcon />}>
          <AlertTitle>Access Denied</AlertTitle>
          <Typography variant="body2">
            {errorMessage || "You do not have permission to access this server."}
          </Typography>
        </Alert>

        {availableServers.length > 0 && (
          <Card>
            <CardContent>
              <Stack spacing={2}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <ServerIcon color="primary" />
                  <Typography variant="h6">
                    Available Servers
                  </Typography>
                </Box>
                
                <Typography variant="body2" color="text.secondary">
                  You have access to the following {availableServers.length} server{availableServers.length !== 1 ? 's' : ''}:
                </Typography>

                <List sx={{ bgcolor: 'background.paper', borderRadius: 1 }}>
                  {availableServers.map((server) => (
                    <ListItem key={server.server_number} disablePadding>
                      <ListItemButton
                        onClick={() => handleServerClick(server)}
                        sx={{
                          borderRadius: 1,
                          '&:hover': {
                            backgroundColor: 'action.hover',
                          },
                        }}
                      >
                        <ListItemText
                          primary={
                            <Typography variant="body1" fontWeight="medium">
                              {server.name}
                            </Typography>
                          }
                          secondary={
                            <Typography variant="caption" color="text.secondary">
                              Server #{server.server_number} • Port {server.port}
                              {server.current && " • Current Server"}
                            </Typography>
                          }
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </Stack>
            </CardContent>
          </Card>
        )}

        {availableServers.length === 0 && (
          <Card>
            <CardContent>
              <Stack spacing={2} alignItems="center">
                <LockIcon sx={{ fontSize: 48, color: 'text.secondary' }} />
                <Typography variant="h6" align="center">
                  No Servers Available
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center">
                  You don't have access to any servers. Please contact your administrator.
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        )}
      </Stack>
    </Box>
  );
}

