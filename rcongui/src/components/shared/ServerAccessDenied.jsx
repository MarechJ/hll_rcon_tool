import { Stack, Typography, Button, CircularProgress, Paper } from "@mui/material";
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

  if (isLoading) {
    return (
      <Stack spacing={2} alignItems="center" justifyContent="center" sx={{ textAlign: "center" }}>
        <CircularProgress />
        <Typography variant="body2" color="text.secondary">
          Loading available servers...
        </Typography>
      </Stack>
    );
  }

  return (
    <Stack spacing={2} alignItems="center" justifyContent="center" sx={{ textAlign: "center" }}>
      <Typography variant="h3">403</Typography>
      <Typography variant="h4">Access Denied</Typography>
      <Typography variant="body1" color="text.secondary">
        You do not have permission to this server.
      </Typography>

      {availableServers.length > 0 && (
        <Paper elevation={4} variant="outlined" sx={{ padding: 2, maxWidth: 500 }}>
          <Stack spacing={2}>
            <Typography variant="h6">Available Servers</Typography>
            {availableServers.map((server) => (
              <Button
                key={server.server_number}
                variant="contained"
                onClick={() => handleServerClick(server)}
              >
                {server.name}
              </Button>
            ))}
          </Stack>
        </Paper>
      )}

      {availableServers.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          You don't have access to any servers. Please contact your administrator.
        </Typography>
      )}

      <Stack direction="row" spacing={2}>
        <Button variant="contained" color="error" onClick={handleLogout}>
          Logout
        </Button>
      </Stack>
    </Stack>
  );
}

