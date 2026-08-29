import { useEffect, useMemo, useState } from "react";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  IconButton,
  LinearProgress,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import dayjs from "dayjs";
import { toast } from "react-toastify";
import { useAuth } from "@/hooks/useAuth";
import VipListDialog from "@/components/VipList/VipListDialog";
import VipListBulkDialog from "@/components/VipList/VipListBulkDialog";
import VipListRecordDialog from "@/components/VipList/VipListRecordDialog";
import { PlayerDrawerLink } from "@/components/shared/PlayerDrawerLink";
import {
  vipListMutationOptions,
  vipListQueryKeys,
  vipListQueryOptions,
} from "@/queries/vip-list-query";

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

const getPlayerIdType = (playerId) => {
  if (/^\d{17}$/.test(playerId)) return "steam64";
  if (/^[0-9a-fA-F]{32}$/.test(playerId)) return "eos";
  return "unknown";
};

const downloadTextFile = (filename, content, type) => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
};

const csvValue = (value) =>
  `"${String(value ?? "").replaceAll('"', '""')}"`;

const exportVipRecords = (format, vipList, records) => {
  const exportedAt = new Date().toISOString();
  const safeName = String(vipList.name)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "") || `vip-list-${vipList.id}`;

  const exportedRecords = records.map((record) => ({
    record_id: record.id,
    vip_list_id: vipList.id,
    vip_list_name: vipList.name,
    player_id: record.player_id,
    player_id_type: getPlayerIdType(record.player_id),
    player_name: record.player_name ?? null,
    manual_name: record.description ?? null,
    notes: record.notes ?? null,
    active: record.is_active,
    expired: record.is_expired,
    expires_at: record.expires_at ?? null,
    added_by: record.admin_name ?? null,
    created_at: record.created_at ?? null,
  }));

  if (format === "json") {
    downloadTextFile(
      `${safeName}-${exportedAt.slice(0, 10)}.json`,
      JSON.stringify(
        {
          schema_version: 1,
          exported_at: exportedAt,
          vip_list: {
            id: vipList.id,
            name: vipList.name,
            sync: vipList.sync,
            servers: vipList.servers,
          },
          records: exportedRecords,
        },
        null,
        2
      ),
      "application/json;charset=utf-8"
    );
    return;
  }

  const columns = Object.keys(exportedRecords[0] ?? {});
  const csv = [
    columns.map(csvValue).join(","),
    ...exportedRecords.map((record) =>
      columns.map((column) => csvValue(record[column])).join(",")
    ),
  ].join("\n");

  downloadTextFile(
    `${safeName}-${exportedAt.slice(0, 10)}.csv`,
    `\uFEFF${csv}`,
    "text/csv;charset=utf-8"
  );
};

function RecordTable({
  title,
  records,
  loading,
  emptyText,
  onEdit,
  onDelete,
  selectable,
  selectedRecordIds,
  onToggleRecord,
  onToggleRecords,
}) {
  const safeRecords = Array.isArray(records) ? records : [];
  const showActions = Boolean(onEdit || onDelete);
  const selectedSet = new Set(selectedRecordIds);
  const selectedVisibleCount = safeRecords.filter((record) =>
    selectedSet.has(record.id)
  ).length;
  const allVisibleSelected =
    safeRecords.length > 0 &&
    selectedVisibleCount === safeRecords.length;
  const someVisibleSelected =
    selectedVisibleCount > 0 && !allVisibleSelected;

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
                {selectable && (
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={allVisibleSelected}
                      indeterminate={someVisibleSelected}
                      onChange={(event) =>
                        onToggleRecords(
                          safeRecords,
                          event.target.checked
                        )
                      }
                      inputProps={{
                        "aria-label": `Select all records in ${title}`,
                      }}
                    />
                  </TableCell>
                )}
                <TableCell>Player</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Expiration</TableCell>
                <TableCell>Added by</TableCell>
                <TableCell>Notes</TableCell>
                {showActions && (
                  <TableCell align="right">Actions</TableCell>
                )}
              </TableRow>
            </TableHead>
            <TableBody>
              {safeRecords.map((record) => {
                const active = record.is_active && !record.is_expired;
                return (
                  <TableRow
                    key={record.id}
                    hover
                    selected={selectedSet.has(record.id)}
                  >
                    {selectable && (
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedSet.has(record.id)}
                          onChange={(event) =>
                            onToggleRecord(
                              record.id,
                              event.target.checked
                            )
                          }
                          inputProps={{
                            "aria-label": `Select VIP record ${record.id}`,
                          }}
                        />
                      </TableCell>
                    )}
                    <TableCell>
                      <Stack spacing={0.25}>
                        {record.player_name ? (
                          <Stack
                            direction="row"
                            spacing={1}
                            alignItems="center"
                            useFlexGap
                            flexWrap="wrap"
                          >
                            <PlayerDrawerLink
                              playerId={record.player_id}
                              sx={{ fontStyle: "normal" }}
                            >
                              {record.player_name}
                            </PlayerDrawerLink>
                            <Chip
                              label="Player database"
                              color="primary"
                              variant="outlined"
                              size="small"
                            />
                          </Stack>
                        ) : record.description ? (
                          <Stack
                            direction="row"
                            spacing={1}
                            alignItems="center"
                            useFlexGap
                            flexWrap="wrap"
                          >
                            <Typography variant="body2">
                              {record.description}
                            </Typography>
                            <Chip
                              label="Manual name"
                              variant="outlined"
                              size="small"
                            />
                          </Stack>
                        ) : (
                          <Typography
                            variant="body2"
                            color="text.secondary"
                          >
                            Unknown player
                          </Typography>
                        )}
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
                    {showActions && (
                      <TableCell align="right">
                        {onEdit && (
                          <Tooltip title="Edit record">
                            <IconButton
                              size="small"
                              onClick={() => onEdit(record)}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        {onDelete && (
                          <Tooltip title="Delete record">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => onDelete(record)}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    )}
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

const hasPermission = (permissions, permission) =>
  Boolean(
    permissions?.is_superuser ||
      permissions?.permissions?.some(
        (entry) => entry.permission === permission
      )
  );

export default function VipListsPage() {
  const queryClient = useQueryClient();
  const { permissions } = useAuth();
  const [selectedListId, setSelectedListId] = useState(null);
  const [listDialog, setListDialog] = useState(null);
  const [recordDialog, setRecordDialog] = useState(null);
  const [bulkDialogOpen, setBulkDialogOpen] = useState(false);
  const [selectedRecordIds, setSelectedRecordIds] = useState([]);
  const [confirmation, setConfirmation] = useState(null);

  const canCreateLists = hasPermission(
    permissions,
    "can_create_vip_lists"
  );
  const canChangeLists = hasPermission(
    permissions,
    "can_change_vip_lists"
  );
  const canDeleteLists = hasPermission(
    permissions,
    "can_delete_vip_lists"
  );
  const canAddRecords = hasPermission(
    permissions,
    "can_add_vip_list_records"
  );
  const canChangeRecords = hasPermission(
    permissions,
    "can_change_vip_list_records"
  );
  const canDeleteRecords = hasPermission(
    permissions,
    "can_delete_vip_list_records"
  );

  const refreshLists = () =>
    queryClient.invalidateQueries({
      queryKey: vipListQueryKeys.lists,
    });

  const refreshRecords = () => {
    if (!Number.isInteger(selectedListId)) return Promise.resolve();

    return Promise.all([
      queryClient.invalidateQueries({
        queryKey: [...vipListQueryKeys.activeRecords, selectedListId],
      }),
      queryClient.invalidateQueries({
        queryKey: [...vipListQueryKeys.inactiveRecords, selectedListId],
      }),
    ]);
  };

  const mutationError = (error) =>
    toast.error(
      error?.message ?? "The VIP list operation failed."
    );

  const createList = useMutation({
    ...vipListMutationOptions.createList,
    onSuccess: async () => {
      toast.success("VIP list created.");
      await refreshLists();
    },
    onError: mutationError,
  });

  const editList = useMutation({
    ...vipListMutationOptions.editList,
    onSuccess: async () => {
      toast.success("VIP list updated.");
      await refreshLists();
    },
    onError: mutationError,
  });

  const deleteList = useMutation({
    ...vipListMutationOptions.deleteList,
    onSuccess: async () => {
      setSelectedListId(null);
      toast.success("VIP list deleted.");
      await refreshLists();
    },
    onError: mutationError,
  });

  const createRecord = useMutation({
    ...vipListMutationOptions.createRecord,
    onSuccess: async () => {
      toast.success("VIP record added.");
      await refreshRecords();
    },
    onError: mutationError,
  });

  const editRecord = useMutation({
    ...vipListMutationOptions.editRecord,
    onSuccess: async () => {
      toast.success("VIP record updated.");
      await refreshRecords();
    },
    onError: mutationError,
  });

  const deleteRecord = useMutation({
    ...vipListMutationOptions.deleteRecord,
    onSuccess: async () => {
      toast.success("VIP record deleted.");
      await refreshRecords();
    },
    onError: mutationError,
  });

  const bulkEditRecords = useMutation({
    ...vipListMutationOptions.bulkEditRecords,
    onSuccess: () => {
      toast.success("Selected VIP records updated.");
    },
    onError: mutationError,
  });

  const bulkDeleteRecords = useMutation({
    ...vipListMutationOptions.bulkDeleteRecords,
    onSuccess: () => {
      toast.success("Selected VIP records deleted.");
    },
    onError: mutationError,
  });

  const submitList = async (data) => {
    if (listDialog?.mode === "edit") {
      await editList.mutateAsync({
        id: listDialog.vipList.id,
        ...data,
      });
    } else {
      const response = await createList.mutateAsync(data);
      const createdList = response?.result ?? response;

      if (Number.isInteger(createdList?.id)) {
        setSelectedListId(createdList.id);
      }
    }

    setListDialog(null);
  };

  const submitRecord = async (data) => {
    if (recordDialog?.mode === "edit") {
      await editRecord.mutateAsync({
        id: recordDialog.record.id,
        ...data,
      });
    } else {
      await createRecord.mutateAsync(data);
    }

    setRecordDialog(null);
  };

  const toggleRecord = (recordId, checked) => {
    setSelectedRecordIds((current) =>
      checked
        ? [...new Set([...current, recordId])]
        : current.filter((id) => id !== recordId)
    );
  };

  const toggleRecords = (records, checked) => {
    const recordIds = records.map((record) => record.id);

    setSelectedRecordIds((current) =>
      checked
        ? [...new Set([...current, ...recordIds])]
        : current.filter((id) => !recordIds.includes(id))
    );
  };

  const submitBulkOperation = async (operation) => {
    if (operation.kind === "export") {
      exportVipRecords(
        operation.format,
        selectedList,
        selectedRecords
      );
      toast.success(
        `Exported ${selectedRecords.length} VIP records.`
      );
      setBulkDialogOpen(false);
      return;
    }

    if (operation.kind === "delete") {
      await bulkDeleteRecords.mutateAsync(operation.recordIds);
    } else {
      const {
        kind,
        action,
        ...data
      } = operation;

      await bulkEditRecords.mutateAsync(data);
    }

    await refreshRecords();
    setSelectedRecordIds([]);
    setBulkDialogOpen(false);
  };

  const confirmDelete = async () => {
    const pendingConfirmation = confirmation;
    setConfirmation(null);

    try {
      if (pendingConfirmation?.kind === "list") {
        await deleteList.mutateAsync(pendingConfirmation.item);
      } else if (pendingConfirmation?.kind === "record") {
        await deleteRecord.mutateAsync(pendingConfirmation.item);
      }
    } catch {
      // The mutation already displays the API error.
    }
  };

  const listMutationPending =
    createList.isPending ||
    editList.isPending ||
    deleteList.isPending;
  const recordMutationPending =
    createRecord.isPending ||
    editRecord.isPending ||
    deleteRecord.isPending ||
    bulkEditRecords.isPending ||
    bulkDeleteRecords.isPending;
  const mutationPending =
    listMutationPending || recordMutationPending;

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

  const selectedRecords = useMemo(() => {
    const selectedSet = new Set(selectedRecordIds);

    return [...activeRecords, ...inactiveRecords].filter((record) =>
      selectedSet.has(record.id)
    );
  }, [activeRecords, inactiveRecords, selectedRecordIds]);

  useEffect(() => {
    setSelectedRecordIds([]);
    setBulkDialogOpen(false);
  }, [selectedListId]);

  if (listsLoading) {
    return (
      <Stack alignItems="center" sx={{ p: 6 }}>
        <CircularProgress />
      </Stack>
    );
  }

  return (
    <Stack spacing={2}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={1}
        alignItems={{ xs: "flex-start", sm: "center" }}
      >
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4">VIP Lists</Typography>
          <Typography color="text.secondary">
            Database-backed VIP lists for HLL and HLL: Vietnam.
          </Typography>
        </Box>

        {canCreateLists && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setListDialog({ mode: "create" })}
          >
            Create list
          </Button>
        )}
      </Stack>

      {mutationPending && <LinearProgress />}

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
                  {canAddRecords && (
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      onClick={() =>
                        setRecordDialog({ mode: "create" })
                      }
                    >
                      Add record
                    </Button>
                  )}
                  {canChangeLists && (
                    <Button
                      startIcon={<EditIcon />}
                      onClick={() =>
                        setListDialog({
                          mode: "edit",
                          vipList: selectedList,
                        })
                      }
                    >
                      Edit list
                    </Button>
                  )}
                  {canDeleteLists && (
                    <Button
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={() =>
                        setConfirmation({
                          kind: "list",
                          item: selectedList,
                        })
                      }
                    >
                      Delete list
                    </Button>
                  )}
                </Stack>
              </Paper>
            )}

            {selectedRecordIds.length > 0 && (
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    spacing={1}
                    alignItems={{ xs: "stretch", sm: "center" }}
                  >
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography fontWeight={600}>
                        {selectedRecordIds.length} records selected
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        Selection includes active, inactive and expired
                        records in this VIP list.
                      </Typography>
                    </Box>
                    <Button
                      onClick={() => setSelectedRecordIds([])}
                      disabled={recordMutationPending}
                    >
                      Clear selection
                    </Button>
                    <Button
                      variant="contained"
                      onClick={() => setBulkDialogOpen(true)}
                      disabled={recordMutationPending}
                    >
                      Bulk actions
                    </Button>
                  </Stack>
                </Paper>
              )}

            <RecordTable
              title="Active records"
              records={activeRecords}
              loading={activeLoading}
              emptyText="This list has no active VIP records."
              selectable
              selectedRecordIds={selectedRecordIds}
              onToggleRecord={toggleRecord}
              onToggleRecords={toggleRecords}
              onEdit={
                canChangeRecords
                  ? (record) =>
                      setRecordDialog({
                        mode: "edit",
                        record,
                      })
                  : undefined
              }
              onDelete={
                canDeleteRecords
                  ? (record) =>
                      setConfirmation({
                        kind: "record",
                        item: record,
                      })
                  : undefined
              }
            />

            <RecordTable
              title="Inactive and expired records"
              records={inactiveRecords}
              loading={inactiveLoading}
              emptyText="This list has no inactive or expired records."
              selectable
              selectedRecordIds={selectedRecordIds}
              onToggleRecord={toggleRecord}
              onToggleRecords={toggleRecords}
              onEdit={
                canChangeRecords
                  ? (record) =>
                      setRecordDialog({
                        mode: "edit",
                        record,
                      })
                  : undefined
              }
              onDelete={
                canDeleteRecords
                  ? (record) =>
                      setConfirmation({
                        kind: "record",
                        item: record,
                      })
                  : undefined
              }
            />
          </Stack>
        </Stack>
      )}

      <VipListBulkDialog
        open={bulkDialogOpen && selectedRecords.length > 0}
        vipList={selectedList}
        vipLists={lists}
        records={selectedRecords}
        canChange={canChangeRecords}
        canDelete={canDeleteRecords}
        loading={
          bulkEditRecords.isPending ||
          bulkDeleteRecords.isPending
        }
        onClose={() => setBulkDialogOpen(false)}
        onSubmit={submitBulkOperation}
      />

      <VipListRecordDialog
        open={Boolean(recordDialog && selectedList)}
        mode={recordDialog?.mode}
        vipList={selectedList}
        initialValues={
          recordDialog?.mode === "edit"
            ? {
                playerId: recordDialog.record.player_id,
                playerName: recordDialog.record.player_name,
                description: recordDialog.record.description,
                notes: recordDialog.record.notes,
                active: recordDialog.record.is_active,
                expiresAt: recordDialog.record.expires_at,
              }
            : undefined
        }
        loading={recordMutationPending}
        onClose={() => setRecordDialog(null)}
        onSubmit={submitRecord}
      />

      <VipListDialog
        open={Boolean(listDialog)}
        initialValues={
          listDialog?.mode === "edit"
            ? {
                name: listDialog.vipList.name,
                sync: listDialog.vipList.sync,
                servers: listDialog.vipList.servers,
              }
            : undefined
        }
        title={
          listDialog?.mode === "edit"
            ? "Edit VIP list"
            : "Create VIP list"
        }
        submitLabel={
          listDialog?.mode === "edit" ? "Save" : "Create list"
        }
        loading={listMutationPending}
        onClose={() => setListDialog(null)}
        onSubmit={submitList}
      />

      <Dialog
        open={Boolean(confirmation)}
        onClose={
          mutationPending ? undefined : () => setConfirmation(null)
        }
      >
        <DialogTitle>
          {confirmation?.kind === "list"
            ? "Delete VIP list?"
            : "Delete VIP record?"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {confirmation?.kind === "list"
              ? `This permanently deletes “${confirmation.item.name}” and all records contained in it. No gameserver synchronization is performed.`
              : `This permanently deletes VIP record #${confirmation?.item?.id}. No gameserver synchronization is performed.`}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setConfirmation(null)}
            disabled={mutationPending}
          >
            Cancel
          </Button>
          <Button
            color="error"
            variant="contained"
            onClick={confirmDelete}
            disabled={mutationPending}
          >
            Delete permanently
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
