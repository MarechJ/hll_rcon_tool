import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import dayjs from "dayjs";
import { vipListQueryOptions } from "@/queries/vip-list-query";

const formatSyncMethod = (value) =>
  String(value ?? "")
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/^./, (character) => character.toUpperCase());

const formatServers = (servers) => {
  if (servers === null) return "All servers";
  if (!servers?.length) return "No servers";
  return servers.map((server) => `#${server}`).join(", ");
};

const formatExpiration = (expiresAt) => {
  if (!expiresAt) return "Never";
  return dayjs(expiresAt).format("YYYY-MM-DD HH:mm");
};

function RecordTable({ title, records, loading, emptyText }) {
  const safeRecords = Array.isArray(records) ? records : [];

  return (
    <Paper component="section" variant="outlined">
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        sx={{ p: 2 }}
      >
        <Typography variant="h6">{title}</Typography>
        <Chip label={safeRecords.length} size="small" />
      </Stack>
      <Divider />

      {loading ? (
        <Stack alignItems="center" sx={{ p: 4 }}>
          <CircularProgress size={28} />
        </Stack>
      ) : safeRecords.length === 0 ? (
        <Typography color="text.secondary" sx={{ p: 3 }}>
          {emptyText}
        </Typography>
      ) : (
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Player</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Expiration</TableCell>
                <TableCell>Added by</TableCell>
                <TableCell>Notes</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {safeRecords.map((record) => {
                const active = record.is_active && !record.is_expired;
                return (
                  <TableRow key={record.id} hover>
                    <TableCell>
                      <Stack spacing={0.25}>
                        <Typography variant="body2">
                          {record.description || "No description"}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{
                            fontFamily: "monospace",
                            overflowWrap: "anywhere",
                          }}
                        >
                          {record.player_id}
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={
                          active
                            ? "Active"
                            : record.is_expired
                            ? "Expired"
                            : "Inactive"
                        }
                        color={
                          active
                            ? "success"
                            : record.is_expired
                            ? "warning"
                            : "default"
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{formatExpiration(record.expires_at)}</TableCell>
                    <TableCell>{record.admin_name || "—"}</TableCell>
                    <TableCell>{record.notes || "—"}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  );
}

export default function VipListsPage() {
  const [selectedListId, setSelectedListId] = useState(null);

  const {
    data: lists = [],
    isLoading: listsLoading,
    error: listsError,
  } = useQuery(vipListQueryOptions.lists());

  useEffect(() => {
    if (
      lists.length > 0 &&
      !lists.some((vipList) => vipList.id === selectedListId)
    ) {
      setSelectedListId(lists[0].id);
    }
  }, [lists, selectedListId]);

  const selectedList = useMemo(
    () => lists.find((vipList) => vipList.id === selectedListId) ?? null,
    [lists, selectedListId]
  );

  const {
    data: activeRecords = [],
    isLoading: activeLoading,
    error: activeError,
  } = useQuery(vipListQueryOptions.activeRecords(selectedListId));

  const {
    data: inactiveRecords = [],
    isLoading: inactiveLoading,
    error: inactiveError,
  } = useQuery(vipListQueryOptions.inactiveRecords(selectedListId));

  const error = listsError || activeError || inactiveError;

  if (listsLoading) {
    return (
      <Stack alignItems="center" sx={{ p: 6 }}>
        <CircularProgress />
      </Stack>
    );
  }

  return (
    <Stack spacing={2}>
      <Stack>
        <Typography variant="h4">VIP Lists</Typography>
        <Typography color="text.secondary">
          Database-backed VIP lists for HLL and HLL: Vietnam.
        </Typography>
      </Stack>

      {error && (
        <Alert severity="error">
          {error.message || "The VIP lists could not be loaded."}
        </Alert>
      )}

      {lists.length === 0 ? (
        <Alert severity="info">No VIP lists have been configured.</Alert>
      ) : (
        <Stack direction={{ xs: "column", lg: "row" }} spacing={2}>
          <Paper
            component="nav"
            variant="outlined"
            sx={{ width: { xs: "100%", lg: 300 }, flexShrink: 0, p: 1 }}
          >
            <Typography variant="subtitle2" sx={{ px: 1, py: 0.5 }}>
              Lists
            </Typography>
            <Stack spacing={0.5}>
              {lists.map((vipList) => (
                <Button
                  key={vipList.id}
                  variant={selectedListId === vipList.id ? "contained" : "text"}
                  color={selectedListId === vipList.id ? "primary" : "inherit"}
                  onClick={() => setSelectedListId(vipList.id)}
                  sx={{
                    justifyContent: "flex-start",
                    textAlign: "left",
                    textTransform: "none",
                  }}
                >
                  <Stack alignItems="flex-start">
                    <Typography variant="body2">{vipList.name}</Typography>
                    <Typography variant="caption">
                      {formatServers(vipList.servers)}
                    </Typography>
                  </Stack>
                </Button>
              ))}
            </Stack>
          </Paper>

          <Stack spacing={2} sx={{ minWidth: 0, flex: 1 }}>
            {selectedList && (
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  spacing={1}
                  alignItems={{ xs: "flex-start", sm: "center" }}
                >
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h5">{selectedList.name}</Typography>
                    <Typography color="text.secondary">
                      {formatServers(selectedList.servers)}
                    </Typography>
                  </Box>
                  <Chip
                    label={formatSyncMethod(selectedList.sync)}
                    variant="outlined"
                  />
                </Stack>
              </Paper>
            )}

            <RecordTable
              title="Active records"
              records={activeRecords}
              loading={activeLoading}
              emptyText="This list has no active VIP records."
            />

            <RecordTable
              title="Inactive and expired records"
              records={inactiveRecords}
              loading={inactiveLoading}
              emptyText="This list has no inactive or expired records."
            />
          </Stack>
        </Stack>
      )}
    </Stack>
  );
}
