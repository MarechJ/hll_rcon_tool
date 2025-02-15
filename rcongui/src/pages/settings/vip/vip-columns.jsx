import { Checkbox, Chip, Stack, Typography } from "@mui/material";
import dayjs from "dayjs";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import { SortableHeader } from "@/components/table/styles";
import CopyableText from "@/components/shared/CopyableText";

const INDEFINITE = "3000-01-01T00:00:00+00:00";

const isIndefinite = (expiration) =>
  expiration === null || expiration === INDEFINITE;
const isActive = (expiration) =>
  expiration === null || dayjs(expiration).isAfter(dayjs());

const vipColumns = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={table.getIsAllRowsSelected()}
        indeterminate={table.getIsSomePageRowsSelected()}
        onChange={table.getToggleAllRowsSelectedHandler()}
        size="small"
        sx={{
          p: 0,
        }}
      />
    ),
    cell: ({ row }) => (
      <div>
        <Checkbox
          checked={row.getIsSelected()}
          disabled={!row.getCanSelect()}
          indeterminate={row.getIsSomeSelected()}
          onChange={row.getToggleSelectedHandler()}
          size="small"
          sx={{
            p: 0,
          }}
        />
      </div>
    ),
    meta: {
      variant: "icon",
    },
  },
  {
    id: "name",
    accessorKey: "name",
    header: SortableHeader("Name"),
    filterFn: "includesString",
    cell: ({ row }) => {
      const { openWithId } = usePlayerSidebar();
      const handleOpenProfile = (playerId) => {
        openWithId(playerId);
      };
      return (
        <Stack>
          <Typography
            variant="body2"
            role="button"
            sx={{
              cursor: "pointer",
              "&:hover": { textDecoration: "underline" },
            }}
            onClick={() => handleOpenProfile(row.original.player_id)}
          >
            {row.original.name}
          </Typography>
          <CopyableText
            text={row.original.player_id}
            size="0.65em"
            sx={{ fontSize: "0.65em", color: "text.secondary" }}
          />
        </Stack>
      );
    },
  },
  {
    id: "status",
    accessorFn: (row) => {
      if (isActive(row.vip_expiration)) {
        return "Active";
      } else {
        return "Expired";
      }
    },
    header: SortableHeader("Status"),
    cell: ({ getValue }) => {
      const status = getValue();
      return (
        <Chip
          label={status}
          color={status === "Active" ? "success" : "error"}
        />
      );
    },
  },
  {
    id: "expires_in_from_now",
    accessorKey: "vip_expiration",
    header: "Expires In/From Now",
    cell: ({ row }) => {
      if (isIndefinite(row.original.vip_expiration)) {
        return "Never";
      }
      return dayjs(row.original.vip_expiration).fromNow();
    },
  },
  {
    id: "player_id",
    accessorKey: "player_id",
    header: "Player ID",
    filterFn: "includesString",
  },
  {
    id: "expiration",
    accessorFn: (row) => {
      if (isIndefinite(row.vip_expiration)) {
        return Number.MAX_SAFE_INTEGER;
      }
      return new Date(row.vip_expiration).getTime();
    },
    header: SortableHeader("Expiration"),
    cell: ({ row }) => {
      if (isIndefinite(row.original.vip_expiration)) {
        return "Indefinite";
      }
      return dayjs(row.original.vip_expiration).format("LLL");
    },
  },
];

export default vipColumns;
