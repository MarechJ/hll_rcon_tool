import { useQuery } from "@tanstack/react-query";
import { Stack, Typography, Button, Paper } from "@mui/material";
import LockIcon from "@mui/icons-material/Lock";
import DnsIcon from "@mui/icons-material/Dns";
import LogoutIcon from "@mui/icons-material/Logout";
import { cmd } from "@/utils/fetchUtils";

export default function ServerAccessDenied() {
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
    window.location.href = server.link;
  };

  const handleLogout = async () => {
    try {
      await cmd.LOGOUT();
    } catch (error) {
      console.error("Logout failed:", error);
    }
    window.location.href = "/login";
  };

  if (isLoading) {
    return (
      <Stack spacing={2} alignItems={"center"} justifyContent={"center"}>
        <Typography variant="body2" color="text.secondary">
          Loading available servers...
        </Typography>
      </Stack>
    );
  }

  return (
    <Stack spacing={2} alignItems={"center"} justifyContent={"center"}>
      <LockIcon sx={{ fontSize: 64, color: "error.main" }} />
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
                startIcon={<DnsIcon />}
                onClick={() => handleServerClick(server)}
                fullWidth
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

      <Button
        variant="contained"
        color="error"
        startIcon={<LogoutIcon />}
        onClick={handleLogout}
      >
        Logout
      </Button>
    </Stack>
  );
}

