import React from "react";
import {
  Alert,
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid2 as Grid,
  Stack,
  Typography,
} from "@mui/material";
import { Cached as CacheIcon, Link as LinkIcon } from "@mui/icons-material";
import { useMutation } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";
import { toast } from "react-toastify";

function CrconAppSettings() {
  // Flush Cache Mutation
  const flushCacheMutation = useMutation({
    mutationFn: () => cmd.CLEAR_APPLICATION_CACHE({ throwRouteError: false }),
    onSuccess: () => {
      toast.success("Cache flushed successfully!");
    },
    onError: (error) => {
      toast.error(`Failed to flush cache: ${error.message}`);
    },
  });

  // Reconnect Gameserver Mutation
  const reconnectMutation = useMutation({
    mutationFn: () => cmd.RECONNECT_GAME_SERVER({ throwRouteError: false }),
    onSuccess: () => {
      toast.success("Reconnected to gameserver successfully!");
    },
    onError: (error) => {
      toast.error(`Failed to reconnect to gameserver: ${error.message}`);
    },
  });

  const handleFlushCache = () => {
    flushCacheMutation.mutate();
  };

  const handleReconnect = () => {
    reconnectMutation.mutate();
  };

  return (
    <Grid container spacing={3}>
      {/* Flush Cache Card */}
      <Grid size={{ xs: 12, md: 6 }}>
        <Card elevation={2}>
          <CardHeader
            avatar={<CacheIcon color="primary" />}
            title="Cache Management"
            subheader="Clear application cache"
          />
          <Divider flexItem sx={{ mt: 1, mb: 2 }} />
          <CardContent>
            <Stack spacing={2}>
              <Typography variant="body2" color="text.secondary">
                Clicking this will flush the internal cache used by different
                CRCON components. Avoid using it unnecessarily, as it forces a
                lot of data to be recalculated and reloaded.
              </Typography>
              <Alert severity="warning">
                Do not use this until instructed to do so by the CRCON
                maintainers or you know what you are doing.
              </Alert>
              <Button
                variant="contained"
                color="warning"
                onClick={handleFlushCache}
                disabled={flushCacheMutation.isPending}
                startIcon={<CacheIcon />}
              >
                {flushCacheMutation.isPending ? "Flushing..." : "Flush Cache"}
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>

      {/* Reconnect Gameserver Card */}
      <Grid size={{ xs: 12, md: 6 }}>
        <Card elevation={2}>
          <CardHeader
            avatar={<LinkIcon color="primary" />}
            title="Gameserver Connection"
            subheader="Reconnect to gameserver"
          />
          <Divider flexItem sx={{ mt: 1, mb: 2 }} />
          <CardContent>
            <Stack spacing={2}>
              <Typography variant="body2" color="text.secondary">
                Force a reconnection to the gameserver. Use this if the
                connection appears to be unstable.
              </Typography>
              <Button
                variant="contained"
                color="primary"
                onClick={handleReconnect}
                disabled={reconnectMutation.isPending}
                startIcon={<LinkIcon />}
              >
                {reconnectMutation.isPending ? "Reconnecting..." : "Reconnect"}
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

export default CrconAppSettings;
