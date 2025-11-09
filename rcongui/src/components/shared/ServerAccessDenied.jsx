import { Box, Card, CardContent, List, ListItem, ListItemButton, ListItemText, Stack, Typography, Alert, AlertTitle, CircularProgress } from "@mui/material";
import LockIcon from "@mui/icons-material/Lock";
import ServerIcon from "@mui/icons-material/Dns";
import { cmd } from "@/utils/fetchUtils";
import { useQuery } from "@tanstack/react-query";

export default function ServerAccessDenied({ errorMessage }) {
  // Fetch accessible servers using the special endpoint that doesn't check current server permissions
  const { data: availableServers = [], isLoading } = useQuery({
    queryKey: ["accessible_servers"],
    queryFn: cmd.GET_ACCESSIBLE_SERVERS,
    retry: 1,
  });

  const handleServerClick = (server) => {
    if (!server.link) {
      console.error("Server has no link:", server);
      return;
    }

    // Navigate to the server's root URL
    window.location.href = server.link;
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

        {isLoading && (
          <Card>
            <CardContent>
              <Stack spacing={2} alignItems="center">
                <CircularProgress />
                <Typography variant="body2" color="text.secondary">
                  Loading available servers...
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        )}

        {!isLoading && availableServers.length > 0 && (
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

        {!isLoading && availableServers.length === 0 && (
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

