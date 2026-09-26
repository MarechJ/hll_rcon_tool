import { useEffect, useMemo, useState } from "react";
import {
  useMutation,
  useQueries,
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
  FormControl,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Tooltip,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import StarIcon from "@mui/icons-material/Star";
import StarBorderIcon from "@mui/icons-material/StarBorder";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import dayjs from "dayjs";
import { toast } from "react-toastify";
import { useAuth } from "@/hooks/useAuth";
import { useGlobalStore } from "@/stores/global-state";
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

const formatDuration = (seconds) => {
  if (seconds === null) return "Never expires";
  if (seconds % 86400 === 0) return `${seconds / 86400} day(s)`;
  if (seconds % 3600 === 0) return `${seconds / 3600} hour(s)`;
  return `${seconds} second(s)`;
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

const csvValue = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;

const exportVipRecords = (format, vipList, records) => {
  const exportedAt = new Date().toISOString();
  const safeName =
    String(vipList.name)
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
  showList = false,
  listNames = {},
}) {
  const [sorting, setSorting] = useState({ field: "player", direction: "asc" });
  const safeRecords = Array.isArray(records) ? records : [];
  const sortedRecords = [...safeRecords].sort((left, right) => {
    const value = (record) => {
      switch (sorting.field) {
        case "list":
          return listNames[record.vip_list_id] ?? "";
        case "status":
          return record.is_expired ? "Expired" : record.is_active ? "Active" : "Inactive";
        case "expiration":
          return record.expires_at ?? "9999";
        case "admin":
          return record.admin_name ?? "";
        default:
          return record.player_name || record.description || record.player_id;
      }
    };
    const result = String(value(left)).localeCompare(String(value(right)), undefined, {
      numeric: true,
      sensitivity: "base",
    });
    return (result || left.id - right.id) * (sorting.direction === "asc" ? 1 : -1);
  });
  const sortHeader = (field, title) => (
    <TableSortLabel
      active={sorting.field === field}
      direction={sorting.field === field ? sorting.direction : "asc"}
      onClick={() => setSorting((current) => ({
        field,
        direction: current.field === field && current.direction === "asc" ? "desc" : "asc",
      }))}
    >
      {title}
    </TableSortLabel>
  );
  const showActions = Boolean(onEdit || onDelete);
  const selectedSet = new Set(selectedRecordIds);
  const selectedVisibleCount = safeRecords.filter((record) =>
    selectedSet.has(record.id)
  ).length;
  const allVisibleSelected =
    safeRecords.length > 0 && selectedVisibleCount === safeRecords.length;
  const someVisibleSelected = selectedVisibleCount > 0 && !allVisibleSelected;

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
                        onToggleRecords(safeRecords, event.target.checked)
                      }
                      inputProps={{
                        "aria-label": `Select all records in ${title}`,
                      }}
                    />
                  </TableCell>
                )}
                <TableCell>{sortHeader("player", "Player")}</TableCell>
                {showList && (
                  <TableCell>{sortHeader("list", "VIP list")}</TableCell>
                )}
                <TableCell>{sortHeader("status", "Status")}</TableCell>
                <TableCell>{sortHeader("expiration", "Expiration")}</TableCell>
                <TableCell>{sortHeader("admin", "Added by")}</TableCell>
                <TableCell>Notes</TableCell>
                {showActions && <TableCell align="right">Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedRecords.map((record) => {
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
                            onToggleRecord(record.id, event.target.checked)
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
                          <Typography variant="body2" color="text.secondary">
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
                    {showList && (
                      <TableCell>
                        {listNames[record.vip_list_id] ?? `List #${record.vip_list_id}`}
                      </TableCell>
                    )}
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
      permissions?.permissions?.some((entry) => entry.permission === permission)
  );

export default function VipListsPage() {
  const queryClient = useQueryClient();
  const { permissions } = useAuth();
  const serverStatus = useGlobalStore((state) => state.status);
  const availableServers = useGlobalStore((state) => state.servers);
  const serverNumber = serverStatus?.server_number;

  const serverOptions = useMemo(() => {
    const options = {};

    if (Array.isArray(availableServers)) {
      for (const server of availableServers) {
        const number = Number(server?.server_number);

        if (Number.isInteger(number)) {
          options[number] =
            server?.name || server?.short_name || `Server #${number}`;
        }
      }
    }

    if (Number.isInteger(serverNumber) && options[serverNumber] === undefined) {
      options[serverNumber] =
        serverStatus?.name ||
        serverStatus?.short_name ||
        `Server #${serverNumber}`;
    }

    return options;
  }, [
    availableServers,
    serverNumber,
    serverStatus?.name,
    serverStatus?.short_name,
  ]);
  const [selectedListId, setSelectedListId] = useState(null);
  const [listDialog, setListDialog] = useState(null);
  const [recordDialog, setRecordDialog] = useState(null);
  const [bulkDialogOpen, setBulkDialogOpen] = useState(false);
  const [selectedRecordIds, setSelectedRecordIds] = useState([]);
  const [recordSearch, setRecordSearch] = useState("");
  const [searchScope, setSearchScope] = useState("selected");
  const [statusFilter, setStatusFilter] = useState("all");
  const [confirmation, setConfirmation] = useState(null);

  const canCreateLists = hasPermission(permissions, "can_create_vip_lists");
  const canChangeLists = hasPermission(permissions, "can_change_vip_lists");
  const canDeleteLists = hasPermission(permissions, "can_delete_vip_lists");
  const canAddRecords = hasPermission(permissions, "can_add_vip_list_records");
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

  const refreshDefaultList = () =>
    queryClient.invalidateQueries({
      queryKey: [...vipListQueryKeys.defaultList, serverNumber ?? "current"],
    });

  const refreshRecords = (listId = selectedListId) => {
    if (!Number.isInteger(listId)) return Promise.resolve();

    return Promise.all([
      queryClient.invalidateQueries({
        queryKey: [...vipListQueryKeys.activeRecords, listId],
      }),
      queryClient.invalidateQueries({
        queryKey: [...vipListQueryKeys.inactiveRecords, listId],
      }),
    ]);
  };

  const mutationError = (error) =>
    toast.error(error?.message ?? "The VIP list operation failed.");

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

  const setDefaultList = useMutation({
    ...vipListMutationOptions.setDefaultList,
    onSuccess: async () => {
      toast.success(
        `Default VIP list set for ${
          Number.isInteger(serverNumber)
            ? `server #${serverNumber}`
            : "the current server"
        }.`
      );
      await refreshDefaultList();
    },
    onError: mutationError,
  });

  const clearDefaultList = useMutation({
    ...vipListMutationOptions.clearDefaultList,
    onSuccess: async () => {
      toast.success(
        `Default VIP list removed for ${
          Number.isInteger(serverNumber)
            ? `server #${serverNumber}`
            : "the current server"
        }.`
      );
      await refreshDefaultList();
    },
    onError: mutationError,
  });

  const deleteList = useMutation({
    ...vipListMutationOptions.deleteList,
    onSuccess: async () => {
      setSelectedListId(null);
      toast.success("VIP list deleted.");
      await Promise.all([refreshLists(), refreshDefaultList()]);
    },
    onError: mutationError,
  });

  const applyExpiration = useMutation({
    ...vipListMutationOptions.applyExpiration,
    onSuccess: async (response) => {
      toast.success(`Updated ${response?.result ?? response} VIP record(s).`);
      await refreshRecords();
    },
    onError: mutationError,
  });

  const createRecord = useMutation({
    ...vipListMutationOptions.createRecord,
    onSuccess: async (_result, data) => {
      toast.success("VIP record added.");
      await refreshRecords(data.vipListId);
    },
    onError: mutationError,
  });

  const editRecord = useMutation({
    ...vipListMutationOptions.editRecord,
    onSuccess: async (_result, data) => {
      toast.success("VIP record updated.");
      await refreshRecords(data.vipListId);
    },
    onError: mutationError,
  });

  const deleteRecord = useMutation({
    ...vipListMutationOptions.deleteRecord,
    onSuccess: async (_result, record) => {
      toast.success("VIP record deleted.");
      await refreshRecords(record.vip_list_id ?? selectedListId);
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
    const { setAsDefault, ...listData } = data;

    if (listDialog?.mode === "edit") {
      await editList.mutateAsync({
        id: listDialog.vipList.id,
        ...listData,
      });
    } else {
      const response = await createList.mutateAsync(listData);
      const createdList = response?.result ?? response;

      if (Number.isInteger(createdList?.id)) {
        setSelectedListId(createdList.id);

        if (setAsDefault) {
          try {
            await setDefaultList.mutateAsync({
              vipListId: createdList.id,
              serverNumber,
            });
          } catch {
            // The list remains created and the mutation displays the error.
          }
        }
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
      setSelectedListId(data.vipListId);
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
      exportVipRecords(operation.format, selectedList, selectedRecords);
      toast.success(`Exported ${selectedRecords.length} VIP records.`);
      setBulkDialogOpen(false);
      return;
    }

    if (operation.kind === "delete") {
      await bulkDeleteRecords.mutateAsync(operation.recordIds);
    } else {
      const { kind, action, ...data } = operation;

      await bulkEditRecords.mutateAsync(data);
    }

    await refreshRecords();
    setSelectedRecordIds([]);
    setBulkDialogOpen(false);
  };

  const confirmAction = async () => {
    const pendingConfirmation = confirmation;
    if (pendingConfirmation?.kind === "apply-expiration") {
      try {
        await applyExpiration.mutateAsync({
          vipListId: pendingConfirmation.item.id,
          expectedExpirationSeconds: pendingConfirmation.item.default_expiration_seconds,
          includeExpired: pendingConfirmation.includeExpired ?? false,
        });
        setConfirmation(null);
      } catch {
        // Keep the preview open so the administrator can review the error.
      }
      return;
    }
    setConfirmation(null);

    try {
      if (pendingConfirmation?.kind === "list") {
        await deleteList.mutateAsync(pendingConfirmation.item);
      } else if (pendingConfirmation?.kind === "record") {
        await deleteRecord.mutateAsync(pendingConfirmation.item);
      } else if (pendingConfirmation?.kind === "set-default") {
        await setDefaultList.mutateAsync({
          vipListId: pendingConfirmation.item.id,
          serverNumber: pendingConfirmation.serverNumber,
        });
      } else if (pendingConfirmation?.kind === "clear-default") {
        await clearDefaultList.mutateAsync(pendingConfirmation.serverNumber);
      }
    } catch {
      // The mutation already displays the API error.
    }
  };

  const listMutationPending =
    createList.isPending ||
    editList.isPending ||
    setDefaultList.isPending ||
    clearDefaultList.isPending ||
    deleteList.isPending;
  const applyExpirationPending = applyExpiration.isPending;
  const recordMutationPending =
    createRecord.isPending ||
    editRecord.isPending ||
    deleteRecord.isPending ||
    bulkEditRecords.isPending ||
    bulkDeleteRecords.isPending;
  const mutationPending = listMutationPending || recordMutationPending || applyExpirationPending;

  const {
    data: lists = [],
    isLoading: listsLoading,
    error: listsError,
  } = useQuery(vipListQueryOptions.lists());

  const {
    data: defaultList = null,
    isLoading: defaultListLoading,
    error: defaultListError,
  } = useQuery(vipListQueryOptions.defaultList(serverNumber));

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

  const searchingAllLists = searchScope === "all" && recordSearch.trim() !== "";
  const allListQueries = useQueries({
    queries: lists.flatMap((list) => [
      {
        ...vipListQueryOptions.activeRecords(list.id),
        enabled: searchingAllLists,
      },
      {
        ...vipListQueryOptions.inactiveRecords(list.id),
        enabled: searchingAllLists,
      },
    ]),
  });
  const allListRecords = allListQueries.flatMap((query, index) =>
    (query.data ?? []).map((record) => ({
      ...record,
      vip_list_id: lists[Math.floor(index / 2)].id,
    }))
  );
  const listNames = Object.fromEntries(lists.map((list) => [list.id, list.name]));

  const error =
    listsError || defaultListError || activeError || inactiveError ||
    (searchingAllLists && allListQueries.find((query) => query.error)?.error);

  const filterRecords = (records) => {
    const search = recordSearch.trim().toLocaleLowerCase();

    return records.filter((record) => {
      const active = record.is_active && !record.is_expired;
      if (statusFilter === "active" && !active) return false;
      if (statusFilter === "expired" && !record.is_expired) return false;
      if (statusFilter === "inactive" && (active || record.is_expired)) return false;
      if (search === "") return true;
      return [
        record.id,
        record.player_id,
        record.player_name,
        record.description,
        record.notes,
        record.admin_name,
        listNames[record.vip_list_id],
      ].some((value) => String(value ?? "").toLocaleLowerCase().includes(search));
    });
  };

  const filteredCurrentRecords = useMemo(
    () => filterRecords([...activeRecords, ...inactiveRecords]),
    [activeRecords, inactiveRecords, recordSearch, statusFilter, lists]
  );
  const filteredAllListRecords = searchingAllLists
    ? filterRecords(allListRecords)
    : [];

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

  const selectedListIsDefault = selectedList?.id === defaultList?.id;
  const selectedListAppliesToCurrentServer =
    !Number.isInteger(serverNumber) ||
    selectedList?.servers === null ||
    selectedList?.servers?.includes(serverNumber);
  const serverLabel = Number.isInteger(serverNumber)
    ? `server #${serverNumber}`
    : "the current server";

  const confirmationIsDelete =
    confirmation?.kind === "list" || confirmation?.kind === "record";
  const confirmationTitle =
    confirmation?.kind === "list"
      ? "Delete VIP list?"
      : confirmation?.kind === "apply-expiration"
      ? "Apply duration to existing VIPs?"
      : confirmation?.kind === "record"
      ? "Delete VIP record?"
      : confirmation?.kind === "set-default"
      ? `Set default for ${
          Number.isInteger(confirmation?.serverNumber)
            ? `server #${confirmation.serverNumber}`
            : "the current server"
        }?`
      : `Remove default for ${
          Number.isInteger(confirmation?.serverNumber)
            ? `server #${confirmation.serverNumber}`
            : "the current server"
        }?`;
  const confirmationText =
    confirmation?.kind === "list"
      ? `This permanently deletes “${confirmation.item.name}” and all records contained in it. No gameserver synchronization is performed.`
      : confirmation?.kind === "apply-expiration"
      ? `${activeRecords.length + (confirmation.includeExpired ? inactiveRecords.filter((record) => record.is_active && record.is_expired).length : 0)} record(s) in “${confirmation.item.name}” will ${confirmation.item.default_expiration_seconds === null ? "be set to never expire" : `expire ${formatDuration(confirmation.item.default_expiration_seconds)} after confirmation`}. Inactive records remain unchanged. Affected gameservers will be notified.`
      : confirmation?.kind === "record"
      ? `This permanently deletes VIP record #${confirmation?.item?.id}. No gameserver synchronization is performed.`
      : confirmation?.kind === "set-default"
      ? `“${
          confirmation?.item?.name
        }” will become the default destination for new VIP records on ${
          Number.isInteger(confirmation?.serverNumber)
            ? `server #${confirmation.serverNumber}`
            : "the current server"
        }. Existing records and the gameserver are not changed.`
      : `${
          Number.isInteger(confirmation?.serverNumber)
            ? `Server #${confirmation.serverNumber}`
            : "The current server"
        } will no longer have a default VIP list. Existing records and the gameserver are not changed.`;

  if (listsLoading || defaultListLoading) {
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
                    <Stack direction="row" spacing={0.75} alignItems="center">
                      <Typography variant="body2">
                        {`${vipList.name} (ID ${vipList.id})`}
                      </Typography>
                      {vipList.id === defaultList?.id && (
                        <Chip
                          icon={<StarIcon />}
                          label={
                            Number.isInteger(serverNumber)
                              ? `Default #${serverNumber}`
                              : "Default"
                          }
                          color="warning"
                          variant="outlined"
                          size="small"
                        />
                      )}
                    </Stack>
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
                    <Typography variant="h5">
                      {`${selectedList.name} (ID ${selectedList.id})`}
                    </Typography>
                    <Typography color="text.secondary">
                      {formatServers(selectedList.servers)}
                    </Typography>
                  </Box>
                  {selectedListIsDefault && (
                    <Chip
                      icon={<StarIcon />}
                      label={`Default for ${serverLabel}`}
                      color="warning"
                      variant="outlined"
                    />
                  )}
                  <Chip
                    label={formatSyncMethod(selectedList.sync)}
                    variant="outlined"
                  />
                  <Chip
                    label={selectedList.expired_retention_days === null
                      ? "Keep expired records"
                      : selectedList.expired_retention_days === 0
                      ? "Delete expired automatically"
                      : `Delete expired after ${selectedList.expired_retention_days} day(s)`}
                    variant="outlined"
                  />
                  <Chip
                    label={selectedList.default_expiration_seconds === null
                      ? "New VIPs: never expire"
                      : `New VIPs: ${formatDuration(selectedList.default_expiration_seconds)}`}
                    variant="outlined"
                  />
                  {(selectedList.flags ?? []).map((flag) => (
                    <Chip key={flag} label={`Flag: ${flag}`} variant="outlined" />
                  ))}
                  {canChangeRecords && (
                    <Button
                      disabled={activeLoading || inactiveLoading ||
                        (activeRecords.length === 0 &&
                          !inactiveRecords.some((record) => record.is_active && record.is_expired))}
                      onClick={() => setConfirmation({ kind: "apply-expiration", item: selectedList })}
                    >
                      Apply duration to existing
                    </Button>
                  )}
                  {canChangeLists &&
                    (selectedListIsDefault ? (
                      <Button
                        color="warning"
                        startIcon={<StarIcon />}
                        onClick={() =>
                          setConfirmation({
                            kind: "clear-default",
                            item: selectedList,
                            serverNumber,
                          })
                        }
                      >
                        Remove default
                      </Button>
                    ) : (
                      <Tooltip
                        title={
                          selectedListAppliesToCurrentServer
                            ? `Use this list for new VIP records on ${serverLabel}`
                            : `This list does not apply to ${serverLabel}`
                        }
                      >
                        <span>
                          <Button
                            startIcon={<StarBorderIcon />}
                            disabled={!selectedListAppliesToCurrentServer}
                            onClick={() =>
                              setConfirmation({
                                kind: "set-default",
                                item: selectedList,
                                serverNumber,
                              })
                            }
                          >
                            Set as default
                          </Button>
                        </span>
                      </Tooltip>
                    ))}
                  {canAddRecords && (
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      onClick={() => setRecordDialog({ mode: "create" })}
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

            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="center">
                <DebouncedSearchInput
                  initialValue={recordSearch}
                  placeholder="Search VIP records"
                  onChange={setRecordSearch}
                  sx={{ flex: 1, width: "100%" }}
                />
                <FormControl size="small" sx={{ minWidth: 160 }}>
                  <InputLabel id="vip-search-scope">Search in</InputLabel>
                  <Select labelId="vip-search-scope" label="Search in" value={searchScope}
                    onChange={(event) => { setSearchScope(event.target.value); setSelectedRecordIds([]); }}>
                    <MenuItem value="selected">Current list</MenuItem>
                    <MenuItem value="all">All lists</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 140 }}>
                  <InputLabel id="vip-record-status">Status</InputLabel>
                  <Select labelId="vip-record-status" label="Status" value={statusFilter}
                    onChange={(event) => setStatusFilter(event.target.value)}>
                    <MenuItem value="all">All</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="inactive">Inactive</MenuItem>
                    <MenuItem value="expired">Expired</MenuItem>
                  </Select>
                </FormControl>
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {searchScope === "all"
                  ? searchingAllLists
                    ? `${filteredAllListRecords.length} matches across ${lists.length} lists`
                    : "Enter a search term to search across all lists."
                  : `${filteredCurrentRecords.length} of ${activeRecords.length + inactiveRecords.length} records shown`}
              </Typography>
            </Paper>

            {searchScope === "selected" && selectedRecordIds.length > 0 && (
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
                    <Typography variant="body2" color="text.secondary">
                      Selection includes active, inactive and expired records in
                      this VIP list.
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
              title={searchScope === "all" ? "Search results across lists" : "VIP records"}
              records={searchScope === "all" ? filteredAllListRecords : filteredCurrentRecords}
              loading={searchScope === "all"
                ? searchingAllLists && allListQueries.some((query) => query.isPending)
                : activeLoading || inactiveLoading}
              emptyText={searchScope === "all" && !searchingAllLists
                ? "Enter a search term to search across all lists."
                : "No VIP records match the selected filters."}
              showList={searchScope === "all"}
              listNames={listNames}
              selectable={searchScope === "selected"}
              selectedRecordIds={selectedRecordIds}
              onToggleRecord={toggleRecord}
              onToggleRecords={toggleRecords}
              onEdit={canChangeRecords
                ? (record) => setRecordDialog({ mode: "edit", record })
                : undefined}
              onDelete={canDeleteRecords
                ? (record) => setConfirmation({ kind: "record", item: record })
                : undefined}
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
        loading={bulkEditRecords.isPending || bulkDeleteRecords.isPending}
        onClose={() => setBulkDialogOpen(false)}
        onSubmit={submitBulkOperation}
      />

      <VipListRecordDialog
        open={Boolean(recordDialog && selectedList)}
        mode={recordDialog?.mode}
        vipList={
          recordDialog?.mode === "edit"
            ? lists.find((list) => list.id === recordDialog.record.vip_list_id) ?? selectedList
            : selectedList
        }
        vipLists={lists}
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
                expiredRetentionDays: listDialog.vipList.expired_retention_days,
                defaultExpirationSeconds: listDialog.vipList.default_expiration_seconds,
                flags: listDialog.vipList.flags,
                servers: listDialog.vipList.servers,
              }
            : undefined
        }
        title={
          listDialog?.mode === "edit" ? "Edit VIP list" : "Create VIP list"
        }
        submitLabel={listDialog?.mode === "edit" ? "Save" : "Create list"}
        loading={listMutationPending}
        serverNumber={serverNumber}
        servers={serverOptions}
        allowDefaultSelection={listDialog?.mode === "create" && canChangeLists}
        onClose={() => setListDialog(null)}
        onSubmit={submitList}
      />

      <Dialog
        open={Boolean(confirmation)}
        onClose={mutationPending ? undefined : () => setConfirmation(null)}
      >
        <DialogTitle>{confirmationTitle}</DialogTitle>
        <DialogContent>
          <DialogContentText>{confirmationText}</DialogContentText>
          {confirmation?.kind === "apply-expiration" && (
            <Stack spacing={1} sx={{ mt: 2 }}>
              <Button
                variant={confirmation.includeExpired ? "contained" : "outlined"}
                color="warning"
                onClick={() => setConfirmation({
                  ...confirmation,
                  includeExpired: !confirmation.includeExpired,
                })}
              >
                {confirmation.includeExpired ? "Include expired: yes" : "Include expired: no"}
              </Button>
              {confirmation.includeExpired && (
                <Alert severity="warning">
                  This also renews expired records that are still marked active.
                </Alert>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setConfirmation(null)}
            disabled={mutationPending}
          >
            Cancel
          </Button>
          <Button
            color={confirmationIsDelete ? "error" : "primary"}
            variant="contained"
            onClick={confirmAction}
            disabled={mutationPending}
          >
            {confirmation?.kind === "apply-expiration"
              ? "Apply to active records"
              : confirmation?.kind === "set-default"
              ? "Set default"
              : confirmation?.kind === "clear-default"
              ? "Remove default"
              : "Delete permanently"}
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
