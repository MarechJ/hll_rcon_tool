import React from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid2 as Grid,
  Stack,
  Typography,
} from "@mui/material";
import SaveIcon from "@mui/icons-material/Save";
import VideoCamIcon from "@mui/icons-material/Videocam";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useLoaderData } from "react-router-dom";
import { cmd } from "@/utils/fetchUtils";
import { toast } from "react-toastify";
import { ToggleInput } from "../components";

const ADMIN_CAM_KEY = {
  broadcast: "broadcast",
  welcome: "welcome",
};

function AdminCamSettings() {
  const loaderData = useLoaderData();
  const queryClient = useQueryClient();

  const { data: cameraConfig } = useQuery({
    queryKey: [{ queryIdentifier: "get_camera_notification_config" }],
    queryFn: () => cmd.GET_CAMERA_NOTIFICATION_CONFIG({ throwRouteError: false }),
    initialData: loaderData.cameraConfig,
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (values) =>
      cmd.SET_CAMERA_NOTIFICATION_CONFIG({ payload: values, throwRouteError: false }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [{ queryIdentifier: "get_camera_notification_config" }],
      });
      toast.success("Admin camera notifications updated successfully!");
    },
    onError: (error) => {
      toast.error(`Failed to update admin camera notifications: ${error.message}`);
    },
  });

  const form = useForm({
    defaultValues: {
      [ADMIN_CAM_KEY.broadcast]: cameraConfig?.[ADMIN_CAM_KEY.broadcast] || false,
      [ADMIN_CAM_KEY.welcome]: cameraConfig?.[ADMIN_CAM_KEY.welcome] || false,
    },
  });

  React.useEffect(() => {
    if (cameraConfig) {
      form.reset({
        [ADMIN_CAM_KEY.broadcast]: cameraConfig[ADMIN_CAM_KEY.broadcast],
        [ADMIN_CAM_KEY.welcome]: cameraConfig[ADMIN_CAM_KEY.welcome],
      });
    }
  }, [cameraConfig, form]);

  const onSubmit = form.handleSubmit((values) => mutate(values));

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 6 }}>
        <Card elevation={2}>
          <CardHeader
            avatar={<VideoCamIcon color="primary" />}
            title="Admin Camera Notifications"
            subheader="Choose how to notify players when admins enter camera mode"
            action={
              <Button
                type="submit"
                form="admin-cam-form"
                variant="contained"
                size="small"
                startIcon={<SaveIcon />}
                disabled={form.formState.isSubmitting || isPending}
              >
                {isPending ? "Saving..." : "Save"}
              </Button>
            }
          />
          <Divider flexItem sx={{ mt: 1, mb: 2 }} />
          <CardContent>
            <Box component="form" id="admin-cam-form" onSubmit={onSubmit}>
              <Stack gap={2}>
                <Typography variant="body1" color="text.secondary">
                  This feature will notify players whenever an admin enters Admin Camera
                  mode.
                  You can choose to send a broadcast message or change the Welcome
                  message. However, it is not recommended to change the Welcome message,
                  as doing so will display the camera message first, followed by the
                  default text a few seconds later. This will obscure the left side of
                  all players' screens twice with each camera entrance.
                </Typography>

                <ToggleInput
                  keyName={ADMIN_CAM_KEY.broadcast}
                  title={"Notify by Broadcast Message"}
                  value={form.watch(ADMIN_CAM_KEY.broadcast)}
                  onChange={(checked) =>
                    form.setValue(ADMIN_CAM_KEY.broadcast, checked)
                  }
                />

                <ToggleInput
                  keyName={ADMIN_CAM_KEY.welcome}
                  title={"Notify by Welcome Message"}
                  value={form.watch(ADMIN_CAM_KEY.welcome)}
                  onChange={(checked) =>
                    form.setValue(ADMIN_CAM_KEY.welcome, checked)
                  }
                />
              </Stack>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

export default AdminCamSettings;