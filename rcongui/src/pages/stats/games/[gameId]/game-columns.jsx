import React from "react";
import {
  Box,
  Checkbox,
  IconButton,
  styled,
} from "@mui/material";
import dayjs from "dayjs";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";
import { CountryFlag } from "@/components/shared/CountryFlag";
import { SortableHeader } from "@/components/table/styles";
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';

export const Square = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "start",
  justifyContent: "center",
  width: 16,
  height: 16,
  lineHeight: "16px",
  fontWeight: "bold",
  backgroundColor: theme.palette.background.paper,
}));

const Center = styled(Box)(() => ({
  display: "grid",
  justifyItems: "center",
  alignContent: "center",
}));

export const columns = [
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
    id: "country",
    header: SortableHeader("🌎"),
    accessorKey: "steaminfo.country",
    cell: ({ row }) => {
      return row.original.steaminfo?.country && row.original.steaminfo?.country !== "private" ? (
        <CountryFlag country={row.original.steaminfo.country} />
      ) : null;
    },
    meta: {
      variant: "icon",
    },
  },
  {
    id: "actions",
    header: "🛠️",
    accessorKey: "actions",
    cell: ({ row }) => {
      return (
        <ActionMenuButton
          actions={generatePlayerActions()}
          recipients={{ name: row.original.player, player_id: row.original.player_id }}
          orientation="horizontal"
          disableRipple={true}
          sx={{
            width: 12,
            height: 12,
          }}
        />
      );
    },
    meta: {
      variant: "icon",
    },
  },
  {
    id: "name",
    header: SortableHeader("Name"),
    accessorKey: "player",
    cell: ({ row }) => {
      return (
        <Box>
          <span>{row.original.player}</span>
        </Box>
      );
    },
    meta: {
      variant: "fullname",
    },
    children: [

    ]
  },
  {
    id: 'expander',
    header: () => null,
    cell: ({ row }) => {
      return row.getCanExpand() ? (
        <IconButton
          size="small"
          sx={{
            p: 0,
            width: 12,
            height: 12,
          }}
          onClick={row.getToggleExpandedHandler()}
        >
          {row.getIsExpanded() ? <ArrowDownwardIcon fontSize="small" /> : <ArrowRightIcon fontSize="small"  />}
        </IconButton>
      ) : (
        '🔵'
      )
    },
  },
  {
    id: "kd",
    header: SortableHeader("K/D"),
    accessorKey: "kill_death_ratio",
    cell: ({ row }) => {
      return <>{row.original.kill_death_ratio}</>;
    },
    meta: {
      variant: "short",
    }
  },
  {
    id: "kpm",
    header: SortableHeader("K/M"),
    accessorKey: "kills_per_minute",
    cell: ({ row }) => {
      return <>{row.original.kills_per_minute}</>;
    },
    meta: {
      variant: "short",
    }
  },
  {
    id: "kills",
    header: SortableHeader("Kills"),
    accessorKey: "kills",
    cell: ({ row }) => {
      return <>{row.original.kills}</>;
    },
    meta: {
      variant: "short",
    }
  },
  {
    id: "deaths",
    header: SortableHeader("Deaths"),
    accessorKey: "deaths",
    cell: ({ row }) => {
      return <>{row.original.deaths}</>;
    },
    meta: {
      variant: "short",
    }
  },
  {
    id: "tk",
    header: SortableHeader("TKs"),
    accessorKey: "teamkills",
    cell: ({ row }) => {
      return <>{row.original.teamkills}</>;
    },
    meta: {
      variant: "short",
    }
  },
  {
    id: "tk_streak",
    header: SortableHeader("TK Streak"),
    accessorKey: "teamkills_streak",
    cell: ({ row }) => {
      return <>{row.original.teamkills_streak}</>;
    },
    meta: {
      variant: "short",
    }
  },
  {
    id: "td",
    header: SortableHeader("TDs"),
    accessorKey: "deaths_by_tk",
    cell: ({ row }) => {
      return <>{row.original.deaths_by_tk}</>;
    },
    meta: {
      variant: "short",
    }
  },
  {
    id: "td_streak",
    header: SortableHeader("TD Streak"),
    accessorKey: "deaths_by_tk_streak",
    cell: ({ row }) => {
      return <>{row.original.deaths_by_tk_streak}</>;
    },
    meta: {
      variant: "short",
    }
  },
  {
    id: "time",
    header: SortableHeader("Time"),
    accessorKey: "time_seconds",
    aggregationFn: "mean",
    cell: ({ row }) => {
      return (
        <>
          {dayjs
            .duration(row.original.time_seconds, "seconds")
            .format("H:mm")}
        </>
      );
    },
    meta: {
      variant: "short",
    },
  },
  {
    id: "player_id",
    header: "Player ID",
    accessorKey: "player_id",
    cell: ({ row }) => {
      return <>{row.original.player_id}</>;
    },
  }
];
