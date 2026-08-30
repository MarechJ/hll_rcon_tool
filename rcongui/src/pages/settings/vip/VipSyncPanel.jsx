import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import SyncIcon from "@mui/icons-material/Sync";
import PreviewIcon from "@mui/icons-material/Preview";
import { useAuth } from "@/hooks/useAuth";
import ConfirmButton from "@/components/shared/ConfirmButton";
import UnknownVipList from "./UnknownVipList";
import VipSyncStatus from "./VipSyncStatus";
import { queryClient } from "@/queryClient";
import {
  vipMutationOptions,
  vipQueryKeys,
  vipQueryOptions,
} from "@/queries/vip-query";

const hasPermission = (permissions, permission) =>
  Boolean(
    permissions?.is_superuser ||
      permissions?.permissions?.some((entry) => entry.permission === permission)
  );

const getErrorMessage = (error, fallback) =>
  error?.message || error?.data?.error || fallback;

const DetailList = ({ title, items, color = "default" }) => {
  if (!items?.length) return null;

  return (
    <Stack spacing={1}>
      <Typography variant="subtitle2">{title}</Typography>
      <Stack direction="row" gap={0.75} flexWrap="wrap">
        {items.map((item) => {
          const playerId = typeof item === "string" ? item : item.player_id;
          const description =
            typeof item === "string" ? null : item.description;

          return (
            <Chip
              key={`${title}-${playerId}`}
              label={description ? `${playerId} — ${description}` : playerId}
              color={color}
              size="small"
              variant="outlined"
              sx={{ maxWidth: "100%" }}
            />
          );
        })}
      </Stack>
    </Stack>
  );
};

const VipSyncPanel = () => {
  const { permissions } = useAuth();
  const canPreview = hasPermission(permissions, "can_view_vip_ids");
  const canSynchronize = hasPermission(permissions, "can_change_vip_lists");
  const [lastExecution, setLastExecution] = useState(null);

  const {
    data: preview,
    error: previewError,
    isFetching: previewLoading,
    refetch: loadPreview,
  } = useQuery(vipQueryOptions.syncPlan());

  const {
    data: syncStatus,
    error: syncStatusError,
    refetch: loadSyncStatus,
  } = useQuery({
    ...vipQueryOptions.syncStatus(),
    enabled: canPreview,
  });

  const {
    mutate: synchronize,
    isPending: synchronizeLoading,
    error: synchronizeError,
  } = useMutation({
    ...vipMutationOptions.synchronize,
    onSuccess: async (result) => {
      setLastExecution(result.execution);

      await queryClient.invalidateQueries({
        queryKey: vipQueryKeys.list,
      });

      await Promise.all([loadPreview(), loadSyncStatus()]);
    },
  });

  const {
    mutate: removeUnknown,
    isPending: removeUnknownLoading,
    variables: removeUnknownVariables,
    error: removeUnknownError,
  } = useMutation({
    ...vipMutationOptions.removeUnknown,
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: vipQueryKeys.list,
      });

      await loadPreview();
    },
  });

  const plan = preview?.plan;
  const additions = plan?.to_add ?? [];
  const removals = plan?.to_remove ?? [];
  const unknown = plan?.unknown ?? [];
  const unchanged = plan?.unchanged ?? [];
  const pendingChanges = additions.length + removals.length;
  const busy = previewLoading || synchronizeLoading || removeUnknownLoading;

  return (
    <Paper component="section" variant="outlined">
      <Stack spacing={2} sx={{ p: 2 }}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          alignItems={{ xs: "stretch", md: "center" }}
          justifyContent="space-between"
          gap={2}
        >
          <Box>
            <Typography variant="h6">VIP synchronization</Typography>
            <Typography variant="body2" color="text.secondary">
              Compare the current gameserver VIPs with all active VIP List
              records. Preview does not change the gameserver.
            </Typography>
          </Box>

          <Stack direction={{ xs: "column", sm: "row" }} gap={1}>
            <Button
              variant="outlined"
              startIcon={
                previewLoading ? (
                  <CircularProgress size={16} />
                ) : (
                  <PreviewIcon />
                )
              }
              onClick={() => {
                setLastExecution(null);
                loadPreview();
              }}
              disabled={!canPreview || busy}
            >
              Preview synchronization
            </Button>

            <ConfirmButton
              buttonText={
                synchronizeLoading ? "Synchronizing..." : "Synchronize now"
              }
              title="Synchronize gameserver VIPs?"
              description={
                `This will add or update ${additions.length} VIP(s) ` +
                `and remove ${removals.length} VIP(s) on this ` +
                "gameserver. VIP List records are not deleted."
              }
              confirmText="Synchronize"
              onConfirm={() => synchronize()}
              disabled={
                !canSynchronize || busy || !plan || pendingChanges === 0
              }
              buttonProps={{
                variant: "contained",
                color: "primary",
                startIcon: <SyncIcon />,
              }}
            />
          </Stack>
        </Stack>

        {!canSynchronize && (
          <Alert severity="info">
            You may preview synchronization, but you do not have permission to
            apply it.
          </Alert>
        )}

        {previewError && (
          <Alert severity="error">
            {getErrorMessage(
              previewError,
              "Could not load the VIP synchronization preview."
            )}
          </Alert>
        )}

        {synchronizeError && (
          <Alert severity="error">
            {getErrorMessage(
              synchronizeError,
              "VIP synchronization could not be started."
            )}
          </Alert>
        )}

        {removeUnknownError && (
          <Alert severity="error">
            {getErrorMessage(
              removeUnknownError,
              "The unknown VIP could not be removed."
            )}
          </Alert>
        )}

        <VipSyncStatus status={syncStatus} error={syncStatusError} />

        {plan && (
          <>
            <Divider />

            <Stack direction="row" gap={1} flexWrap="wrap">
              <Chip
                label={`${additions.length} add or update`}
                color={additions.length ? "success" : "default"}
              />
              <Chip
                label={`${removals.length} remove`}
                color={removals.length ? "error" : "default"}
              />
              <Chip
                label={`${unknown.length} unknown`}
                color={unknown.length ? "warning" : "default"}
              />
              <Chip label={`${unchanged.length} unchanged`} color="info" />
            </Stack>

            {pendingChanges === 0 && unknown.length === 0 && (
              <Alert severity="success">
                The gameserver VIP state already matches the configured VIP
                lists.
              </Alert>
            )}

            {pendingChanges === 0 && unknown.length > 0 && (
              <Alert severity="warning">
                No managed changes are pending. Unknown gameserver VIPs are
                ignored by the current list synchronization mode and can be
                removed individually below.
              </Alert>
            )}

            <DetailList
              title="Add or update on gameserver"
              items={additions}
              color="success"
            />
            <DetailList
              title="Remove from gameserver"
              items={removals}
              color="error"
            />
            <UnknownVipList
              items={unknown}
              canRemove={canSynchronize}
              busy={busy}
              removingPlayerId={removeUnknownVariables?.player_id}
              onRemove={(playerId) => removeUnknown({ player_id: playerId })}
            />
          </>
        )}

        {lastExecution && (
          <>
            <Divider />

            <Alert severity={lastExecution.successful ? "success" : "warning"}>
              {lastExecution.successful
                ? `Synchronization completed: ${lastExecution.added.length} added or updated, ${lastExecution.removed.length} removed.`
                : `Synchronization completed with ${lastExecution.failures.length} failure(s).`}
            </Alert>

            {lastExecution.failures?.map((failure) => (
              <Alert
                key={`${failure.action}-${failure.player_id}`}
                severity="error"
              >
                {failure.action.toUpperCase()} {failure.player_id}:{" "}
                {failure.error}
              </Alert>
            ))}
          </>
        )}
      </Stack>
    </Paper>
  );
};

export default VipSyncPanel;
