import {
  Avatar,
  Box,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import TimerOffIcon from "@mui/icons-material/TimerOff";
import AnnouncementIcon from "@mui/icons-material/Announcement";
import { Link as RouterLink } from "react-router-dom";
import { useMemo, useState } from "react";
import moment from "moment";
import {
  getCoreRowModel,
  getExpandedRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import Table from "@/components/table/Table";
import { SortableHeader } from "@/components/table/styles";
import CopyableText from "@/components/shared/CopyableText";
import makePlayerProfileUrl from "@/utils/makePlayerProfileUrl";

const CARD_REASON_PREVIEW_LENGTH = 120;

function playerName(record) {
  return record.player?.names?.[0]?.name ?? record.player_id ?? "Unknown player";
}

function playerAvatar(record) {
  return record.player?.steaminfo?.profile?.avatar;
}

function PlayerIdentity({ record, compact = false }) {
  const name = playerName(record);

  return (
    <Stack sx={{ minWidth: 0 }}>
      <Typography
        textOverflow="ellipsis"
        fontSize={compact ? "0.875rem" : "1.125rem"}
        fontWeight={600}
        lineHeight={compact ? "1.15rem" : "1.25rem"}
        marginBottom={0.2}
        sx={{ overflowWrap: "anywhere" }}
      >
        <RouterLink
          style={{ color: "inherit" }}
          to={`/records/players/${record.player_id}`}
        >
          {name}
        </RouterLink>
      </Typography>
      <Box sx={{ display: "flex", alignItems: "center", mb: 0.75 }}>
        <CopyableText
          text={record.player_id}
          size="0.75rem"
          sx={{ color: (theme) => theme.palette.text.secondary }}
        />
      </Box>
    </Stack>
  );
}

function formatDate(value) {
  return value ? moment(value).format("MMM D, YYYY HH:mm") : "Never";
}

function trimReason(reason = "", maxLength = CARD_REASON_PREVIEW_LENGTH) {
  return reason.length > maxLength
    ? `${reason.slice(0, maxLength - 1)}…`
    : reason;
}

function reportTemplate(record) {
  const names = (record.player?.names ?? []).map((entry) => entry.name).filter(Boolean);
  const name = names[0] ?? record.player_id;
  return [
    `Name: ${name}`,
    `Aliases: ${names.join(" | ")}`,
    `Player ID: ${record.player_id}`,
    `Steam URL: ${makePlayerProfileUrl(record.player_id, name) ?? "Unknown"}`,
    `HLL Records: https://hllrecords.com/profiles/${record.player_id}`,
    "Type of issue:",
    "Description:",
    "Evidence:",
  ].join("\n");
}

function copyReportTemplate(record) {
  if (!navigator.clipboard) {
    alert("Copying report templates requires HTTPS.");
    return;
  }
  navigator.clipboard.writeText(reportTemplate(record));
}

function RecordActions({ record, onEdit, onExpire, onDelete, align = "center" }) {
  return (
    <Stack direction="row" justifyContent={align} spacing={0.5} sx={{ my: 0.5 }}>
      <Tooltip title="Edit record"><IconButton size="small" color="primary" onClick={() => onEdit(record)}><EditIcon fontSize="small" /></IconButton></Tooltip>
      <Tooltip title={record.is_active ? "Expire record" : "Record is expired"}>
        <span><IconButton size="small" color="warning" disabled={!record.is_active} onClick={() => onExpire(record)}><TimerOffIcon fontSize="small" /></IconButton></span>
      </Tooltip>
      <Tooltip title="Delete record"><IconButton size="small" color="error" onClick={() => onDelete(record)}><DeleteIcon fontSize="small" /></IconButton></Tooltip>
      <Divider orientation="vertical" flexItem sx={{ mx: 0.5, my: 0.5 }} />
      <Tooltip title="Copy report template to clipboard">
        <IconButton size="small" color="info" onClick={() => copyReportTemplate(record)}>
          <AnnouncementIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </Stack>
  );
}

function RecordReasonDialog({ record, onClose }) {
  return (
    <Dialog open={Boolean(record)} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Blacklist reason</DialogTitle>
      <DialogContent>
        <Typography sx={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>
          {record?.formatted_reason ?? record?.reason}
        </Typography>
      </DialogContent>
    </Dialog>
  );
}

export function BlacklistRecordCards({ records, onEdit, onExpire, onDelete }) {
  const [reasonRecord, setReasonRecord] = useState(null);

  if (records.length === 0) {
    return <Typography color="text.secondary" sx={{ py: 4, textAlign: "center" }}>No blacklist records match this search.</Typography>;
  }

  return (
    <>
      <Grid container spacing={1}>
        {records.map((record) => {
          const name = playerName(record);
          const reason = record.formatted_reason ?? record.reason ?? "";
          return (
            <Grid key={record.id} size={{ xs: 12, md: 6, xl: 4 }}>
              <Card variant="outlined" sx={{ height: "100%", opacity: record.is_active ? 1 : 0.7 }}>
                <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <Avatar src={playerAvatar(record)}>{name[0]?.toUpperCase()}</Avatar>
                    <Box sx={{ minWidth: 0, flex: 1 }}>
                      <PlayerIdentity record={record} />
                    </Box>
                    <Chip size="small" color={record.is_active ? "primary" : "default"} label={record.is_active ? "Active" : "Expired"} />
                  </Stack>
                  <RecordActions record={record} onEdit={onEdit} onExpire={onExpire} onDelete={onDelete} align="flex-start" />
                  <Stack spacing={0.25} alignItems="flex-start" sx={{ mb: 1.25 }}>
                    <Typography variant="body2">Expires at {formatDate(record.expires_at)}</Typography>
                    <Typography variant="body2">Blacklist: {record.blacklist?.name ?? "Unknown list"}</Typography>
                  </Stack>
                  <Typography
                    component="button"
                    type="button"
                    onClick={() => setReasonRecord(record)}
                    title="Show the full reason"
                    sx={{
                      display: "block", width: "100%", minHeight: "3.75rem", p: 0,
                      color: "text.primary", bgcolor: "transparent", border: 0, textAlign: "left",
                      font: "inherit", cursor: "pointer", whiteSpace: "pre-line", overflowWrap: "anywhere",
                    }}
                  >
                    {trimReason(reason)}
                  </Typography>
                  <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" gap={0.5} sx={{ mt: 1.25 }}>
                    <Typography variant="caption" color="text.secondary">Added {formatDate(record.created_at)}{record.admin_name ? ` by ${record.admin_name}` : ""}</Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
      <RecordReasonDialog record={reasonRecord} onClose={() => setReasonRecord(null)} />
    </>
  );
}

export function BlacklistRecordsTable({ records, isLoading, isFetching, onEdit, onExpire, onDelete }) {
  const columns = useMemo(() => [
    {
      id: "expand",
      header: "",
      cell: ({ row }) => (
        <IconButton size="small" color="primary" onClick={row.getToggleExpandedHandler()} aria-label={row.getIsExpanded() ? "Hide details" : "Show details"}>
          {row.getIsExpanded() ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      ),
      enableSorting: false,
      meta: { variant: "icon" },
    },
    {
      id: "player",
      accessorFn: playerName,
      header: SortableHeader("Player"),
      cell: ({ row }) => <PlayerIdentity record={row.original} compact />,
      meta: { variant: "recordPlayer" },
    },
    {
      id: "blacklist",
      accessorFn: (record) => record.blacklist?.name ?? "",
      header: SortableHeader("Blacklist"),
      cell: ({ getValue }) => (
        <Typography variant="body2" noWrap title={getValue()}>{getValue()}</Typography>
      ),
      meta: { variant: "recordList" },
    },
    {
      accessorKey: "admin_name",
      header: SortableHeader("Admin"),
      cell: ({ getValue }) => <Typography variant="body2" noWrap>{getValue() || "—"}</Typography>,
      meta: { variant: "recordAdmin" },
    },
    {
      accessorKey: "created_at",
      header: SortableHeader("Created"),
      cell: ({ getValue }) => <Typography variant="body2" noWrap>{formatDate(getValue())}</Typography>,
      sortingFn: "datetime",
      meta: { variant: "recordDate" },
    },
    {
      accessorKey: "expires_at",
      header: SortableHeader("Expires"),
      cell: ({ getValue }) => <Typography variant="body2" noWrap>{formatDate(getValue())}</Typography>,
      sortingFn: "datetime",
      meta: { variant: "recordExpiry" },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => <RecordActions record={row.original} onEdit={onEdit} onExpire={onExpire} onDelete={onDelete} />,
      enableSorting: false,
      meta: { variant: "recordActions" },
    },
  ], [onDelete, onEdit, onExpire]);

  const table = useReactTable({
    data: records,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    getRowCanExpand: () => true,
  });

  return (
    <Table
      table={table}
      config={{ density: "default", fontSize: "small", expandedView: true }}
      isLoading={isLoading}
      isFetching={isFetching}
      renderSubComponent={({ row }) => (
        <Stack spacing={1} sx={{ p: 1.5 }}>
          <Typography variant="subtitle2">Full reason</Typography>
          <Typography sx={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>
            {row.original.formatted_reason ?? row.original.reason}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Record #{row.original.id} · {row.original.is_active ? "Active" : "Expired"} · Created {formatDate(row.original.created_at)} · Expires {formatDate(row.original.expires_at)}
          </Typography>
        </Stack>
      )}
    />
  );
}
