import { Box, Card, CardContent, Stack, Typography, CircularProgress, Button } from "@mui/material";
import LockIcon from "@mui/icons-material/Lock";
import ServerIcon from "@mui/icons-material/Dns";
import LogoutIcon from "@mui/icons-material/Logout";
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

  const handleLogout = async () => {
    try {
      await cmd.LOGOUT();
      window.location.href = "/login";
    } catch (error) {
      console.error("Logout failed:", error);
      // Force redirect to login even if logout fails
      window.location.href = "/login";
    }
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
      <Stack spacing={3} sx={{ maxWidth: 600, width: "100%", alignItems: "center" }}>
        {/* Access Denied Icon and Message */}
        <Stack spacing={2} alignItems="center">
          <LockIcon sx={{ fontSize: 64, color: "error.main" }} />
          <Typography variant="h5" fontWeight="bold" align="center">
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" align="center">
            You do not have permission to this server.
          </Typography>
        </Stack>

        {isLoading && (
          <Card sx={{ width: "100%" }}>
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
          <Card sx={{ width: "100%" }}>
            <CardContent>
              <Stack spacing={3}>
                <Stack direction="row" alignItems="center" justifyContent="center" gap={1}>
                  <ServerIcon color="primary" />
                  <Typography variant="h6">Available Servers</Typography>
                </Stack>

                <Stack spacing={2}>
                  {availableServers.map((server) => (
                    <Button
                      key={server.server_number}
                      variant="contained"
                      size="large"
                      startIcon={<ServerIcon />}
                      onClick={() => handleServerClick(server)}
                      fullWidth
                      sx={{
                        justifyContent: "flex-start",
                        textTransform: "none",
                        py: 1.5,
                      }}
                    >
                      <Stack spacing={0.5} alignItems="flex-start" sx={{ width: "100%" }}>
                        <Typography variant="body1" fontWeight="medium">
                          {server.name}
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                          Server #{server.server_number} • Port {server.port}
                        </Typography>
                      </Stack>
                    </Button>
                  ))}
                </Stack>

                <Button
                  variant="outlined"
                  color="error"
                  size="large"
                  startIcon={<LogoutIcon />}
                  onClick={handleLogout}
                  fullWidth
                  sx={{ textTransform: "none" }}
                >
                  Logout
                </Button>
              </Stack>
            </CardContent>
          </Card>
        )}

        {!isLoading && availableServers.length === 0 && (
          <Card sx={{ width: "100%" }}>
            <CardContent>
              <Stack spacing={3} alignItems="center">
                <Typography variant="h6" align="center">
                  No Servers Available
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center">
                  You don't have access to any servers. Please contact your administrator.
                </Typography>

                <Button
                  variant="outlined"
                  color="error"
                  size="large"
                  startIcon={<LogoutIcon />}
                  onClick={handleLogout}
                  fullWidth
                  sx={{ textTransform: "none" }}
                >
                  Logout
                </Button>
              </Stack>
            </CardContent>
          </Card>
        )}
      </Stack>
    </Box>
  );
}

