import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  LinearProgress,
  Paper,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import GridViewIcon from "@mui/icons-material/GridView";
import TableRowsIcon from "@mui/icons-material/TableRows";
import Pagination from "@mui/material/Pagination";
import { useCallback, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import BlacklistRecordCreateDialog from "@/components/Blacklist/BlacklistRecordCreateDialog";
import BlacklistListCreateDialog from "@/components/Blacklist/BlacklistListCreateDialog";
import BlacklistFilters from "./BlacklistFilters";
import BlacklistListPanel from "./BlacklistListPanel";
import {
  BlacklistRecordCards,
  BlacklistRecordsTable,
} from "./BlacklistRecordViews";
import {
  blacklistMutationOptions,
  blacklistQueryKeys,
  blacklistQueryOptions,
  getBlacklistRecordFilters,
} from "./queries";
import { useAppStore } from "@/stores/app-state";

const mutationError = (error) =>
  toast.error(error?.message ?? "The blacklist operation failed.");

export default function BlacklistRecords() {
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const filters = getBlacklistRecordFilters(searchParams);
  const view = useAppStore((state) => state.blacklistView);
  const setView = useAppStore((state) => state.setBlacklistView);
  const [recordDialog, setRecordDialog] = useState(null);
  const [listDialog, setListDialog] = useState(null);
  const [confirmation, setConfirmation] = useState(null);

  const { data: blacklists = [] } = useQuery(blacklistQueryOptions.lists());
  const { data: servers = {} } = useQuery(blacklistQueryOptions.servers());
  const {
    data: recordPage = { records: [], total: 0 },
    isLoading,
    isFetching,
    error,
  } = useQuery(blacklistQueryOptions.records(filters));

  const refreshRecords = () =>
    queryClient.invalidateQueries({
      queryKey: [{ queryIdentifier: "get_blacklist_records" }],
    });
  const refreshLists = () => {
    queryClient.invalidateQueries({ queryKey: blacklistQueryKeys.lists });
    refreshRecords();
  };

  const createList = useMutation({
    ...blacklistMutationOptions.createList,
    onSuccess: () => {
      toast.success("Blacklist created.");
      refreshLists();
    },
    onError: mutationError,
  });
  const editList = useMutation({
    ...blacklistMutationOptions.editList,
    onSuccess: () => {
      toast.success("Blacklist updated.");
      refreshLists();
    },
    onError: mutationError,
  });
  const deleteList = useMutation({
    ...blacklistMutationOptions.deleteList,
    onSuccess: () => {
      toast.success("Blacklist deleted.");
      refreshLists();
    },
    onError: mutationError,
  });
  const createRecord = useMutation({
    ...blacklistMutationOptions.createRecord,
    onSuccess: () => {
      toast.success("Blacklist record created.");
      refreshRecords();
    },
    onError: mutationError,
  });
  const editRecord = useMutation({
    ...blacklistMutationOptions.editRecord,
    onSuccess: () => {
      toast.success("Blacklist record updated.");
      refreshRecords();
    },
    onError: mutationError,
  });
  const expireRecord = useMutation({
    ...blacklistMutationOptions.expireRecord,
    onSuccess: () => {
      toast.success("Blacklist record expired.");
      refreshRecords();
    },
    onError: mutationError,
  });
  const deleteRecord = useMutation({
    ...blacklistMutationOptions.deleteRecord,
    onSuccess: () => {
      toast.success("Blacklist record deleted.");
      refreshRecords();
    },
    onError: mutationError,
  });

  const setFilters = (nextFilters) => {
    const nextParams = new URLSearchParams();
    Object.entries(nextFilters).forEach(([key, value]) => {
      if (
        value !== "" &&
        value !== false &&
        value !== null &&
        value !== undefined
      ) {
        nextParams.set(key, String(value));
      }
    });
    setSearchParams(nextParams);
  };

  const openRecordEditor = useCallback(
    (record) =>
      setRecordDialog({
        mode: "edit",
        record,
        initialValues: {
          recordId: record.id,
          blacklistId: record.blacklist?.id,
          playerId: record.player_id,
          expiresAt: record.expires_at,
          reason: record.reason,
        },
      }),
    []
  );
  const requestExpire = useCallback(
    (record) => setConfirmation({ kind: "expire-record", item: record }),
    []
  );
  const requestDeleteRecord = useCallback(
    (record) => setConfirmation({ kind: "delete-record", item: record }),
    []
  );

  const submitRecord = (data) => {
    if (recordDialog?.mode === "edit")
      editRecord.mutate({ id: recordDialog.record.id, ...data });
    else createRecord.mutate(data);
  };
  const submitList = (data) => {
    if (listDialog?.mode === "edit")
      editList.mutate({ id: listDialog.blacklist.id, ...data });
    else createList.mutate(data);
  };
  const confirmAction = () => {
    if (confirmation.kind === "delete-list")
      deleteList.mutate(confirmation.item);
    if (confirmation.kind === "delete-record")
      deleteRecord.mutate(confirmation.item);
    if (confirmation.kind === "expire-record")
      expireRecord.mutate(confirmation.item);
    setConfirmation(null);
  };

  const totalPages = Math.max(
    1,
    Math.ceil(Number(recordPage.total ?? 0) / filters.page_size)
  );
  const records = recordPage.records ?? [];
  const mutationPending = [
    createList,
    editList,
    deleteList,
    createRecord,
    editRecord,
    expireRecord,
    deleteRecord,
  ].some((mutation) => mutation.isPending);

  return (
    <Stack spacing={1.5} sx={{ mt: 2 }}>
      <Box sx={{ height: 2 }}>
        {mutationPending && <LinearProgress sx={{ height: 2 }} />}
      </Box>
      {error && <Alert severity="error">{error.message}</Alert>}
      <Stack
        direction={{ xs: "column", lg: "row" }}
        spacing={1.5}
        alignItems="flex-start"
      >
        <Stack
          component="aside"
          spacing={1.5}
          sx={{ width: { xs: "100%", lg: 320 }, flexShrink: 0 }}
        >
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Search records
            </Typography>
            <BlacklistFilters
              filters={filters}
              blacklists={blacklists}
              disabled={isFetching}
              onSubmit={setFilters}
            />
          </Paper>
          <BlacklistListPanel
            blacklists={blacklists}
            servers={servers}
            onCreate={() => setListDialog({ mode: "create" })}
            onEdit={(blacklist) => setListDialog({ mode: "edit", blacklist })}
            onDelete={(blacklist) =>
              setConfirmation({ kind: "delete-list", item: blacklist })
            }
          />
        </Stack>

        <Stack component="main" spacing={1} sx={{ width: "100%", minWidth: 0 }}>
          <Paper variant="outlined" sx={{ p: 1 }}>
            <Stack
              direction="row"
              alignItems="center"
              justifyContent="space-between"
              gap={1}
            >
              <ToggleButtonGroup
                exclusive
                size="small"
                value={view}
                onChange={(_, value) => value && setView(value)}
                aria-label="Record view"
              >
                <ToggleButton value="cards">
                  <GridViewIcon sx={{ mr: { xs: 0, sm: 1 } }} />
                  <Box
                    component="span"
                    sx={{ display: { xs: "none", sm: "inline" } }}
                  >
                    Card view
                  </Box>
                </ToggleButton>
                <ToggleButton value="table">
                  <TableRowsIcon sx={{ mr: { xs: 0, sm: 1 } }} />
                  <Box
                    component="span"
                    sx={{ display: { xs: "none", sm: "inline" } }}
                  >
                    Table view
                  </Box>
                </ToggleButton>
              </ToggleButtonGroup>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setRecordDialog({ mode: "create" })}
              >
                New record
              </Button>
            </Stack>
          </Paper>

          <Box sx={{ height: 2 }}>
            {isFetching && view === "cards" && (
              <LinearProgress sx={{ height: 2 }} />
            )}
          </Box>
          {view === "cards" ? (
            <BlacklistRecordCards
              records={records}
              onEdit={openRecordEditor}
              onExpire={requestExpire}
              onDelete={requestDeleteRecord}
            />
          ) : (
            <BlacklistRecordsTable
              records={records}
              isLoading={isLoading}
              isFetching={isFetching}
              onEdit={openRecordEditor}
              onExpire={requestExpire}
              onDelete={requestDeleteRecord}
            />
          )}

          <Stack
            direction="row"
            alignItems="center"
            justifyContent="space-between"
            gap={1}
            flexWrap="wrap"
            sx={{ pt: 1 }}
          >
            <Typography variant="body2" color="text.secondary">
              {Number(recordPage.total ?? 0).toLocaleString()} records
            </Typography>
            <Pagination
              count={totalPages}
              page={Math.min(filters.page, totalPages)}
              onChange={(_, page) => setFilters({ ...filters, page })}
              disabled={isFetching}
              showFirstButton
              showLastButton
            />
          </Stack>
        </Stack>
      </Stack>

      <BlacklistRecordCreateDialog
        open={Boolean(recordDialog)}
        setOpen={(open) => !open && setRecordDialog(null)}
        blacklists={blacklists}
        onSubmit={submitRecord}
        initialValues={recordDialog?.initialValues}
        titleText={
          recordDialog?.mode === "edit"
            ? "Edit Blacklist Record"
            : "Create Blacklist Record"
        }
        submitText={recordDialog?.mode === "edit" ? "Save" : "Create Record"}
        disablePlayerId={recordDialog?.mode === "edit"}
      />
      <BlacklistListCreateDialog
        open={Boolean(listDialog)}
        setOpen={(open) => !open && setListDialog(null)}
        servers={servers}
        onSubmit={submitList}
        initialValues={
          listDialog?.mode === "edit"
            ? {
                name: listDialog.blacklist.name,
                servers: listDialog.blacklist.servers,
                syncMethod: listDialog.blacklist.sync,
              }
            : undefined
        }
        titleText={
          listDialog?.mode === "edit" ? "Edit Blacklist" : "Create Blacklist"
        }
        submitText={listDialog?.mode === "edit" ? "Save" : "Create List"}
      />
      <Dialog
        open={Boolean(confirmation)}
        onClose={() => setConfirmation(null)}
      >
        <DialogTitle>
          {confirmation?.kind === "expire-record"
            ? "Expire blacklist record?"
            : "Permanently delete?"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {confirmation?.kind === "delete-list"
              ? `This will permanently delete “${confirmation.item.name}” and all its records.`
              : confirmation?.kind === "delete-record"
              ? `This will permanently delete record #${confirmation.item.id}.`
              : "The player will no longer be actively blacklisted by this record."}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmation(null)}>Cancel</Button>
          <Button
            color={confirmation?.kind === "expire-record" ? "warning" : "error"}
            onClick={confirmAction}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
