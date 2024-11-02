import React from "react";
import { CountryFlag } from "@/components/CountryFlag";
import {
  Box,
  Button,
  Checkbox,
  Stack,
  styled,
  Tooltip,
  Typography,
} from "@mui/material";
import { Star, Warning } from "@mui/icons-material";
import { blue, green, purple, red, yellow } from "@mui/material/colors";
import dayjs from "dayjs";
import {
  ActionMenu,
  ActionMenuButton,
} from "@/features/player-action/ActionMenu";
import { playerGameActions } from "@/features/player-action/actions";
import { useActionDialog } from "@/hooks/useActionDialog";
import { HeaderButton, TextButton } from "./styled-table";

function getPlayerTier(level) {
  if (level < 20) {
    return "Novice";
  } else if (level >= 20 && level < 75) {
    return "Apprentice";
  } else if (level >= 75 && level < 200) {
    return "Expert";
  } else if (level >= 200 && level < 350) {
    return "Master";
  } else {
    return "Legend";
  }
}

function hasRecentWarnings(received_actions) {
  const warningsFrom = dayjs().subtract(1, "day").toISOString();
  const warnings = received_actions.filter(
    (action) => action.time > warningsFrom
  );
  return warnings.length > 0;
}

const tierColors = {
  Novice: red[500],
  Apprentice: yellow[500],
  Expert: green[500],
  Master: blue[500],
  Legend: purple[500],
};

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

const LevelColored = styled(Box, {
  shouldForwardProp: (prop) => prop !== "level",
})((styledProps) => {
  const level = styledProps.level;
  if (!level) return {};
  const tier = getPlayerTier(level);
  const color = tierColors[tier];
  return {
    color,
  };
});

const SortableHeader =
  (text) =>
  ({ column }) => {
    return (
      <HeaderButton onClick={column.getToggleSortingHandler()}>
        {text}
      </HeaderButton>
    );
  };

// ... keep playerToRow function as is ...
export const columns = [
  {
    id: "select",
    // TODO: Add a toggle for selecting all rows
    // The table is enabled for column grouping
    // So we need to make sure the select all toggle is working correctly with the grouping
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
  },
  {
    accessorKey: "team",
    id: "team",
    header: SortableHeader("T"),
    cell: ({ row, table }) => {
      return (
        <Square>
          <img
            src={`/icons/teams/${
              row.original.team === "axis" ? "ger" : "us"
            }.webp`}
            width={16}
            height={16}
          />
        </Square>
      );
    },
  },
  {
    id: "unit",
    header: SortableHeader("U"),
    accessorKey: "unit_name",
    // Group by unit name and team
    // getGroupingValue: (row) => `${row.original.unit_name ?? "-"}-${row.original.team}`,
    cell: ({ row }) => {
      return (
        <Square>
          {row.original.unit_name?.charAt(0)?.toUpperCase() ?? "-"}
        </Square>
      );
    },
  },
  {
    id: "role",
    header: SortableHeader("R"),
    accessorKey: "role",
    cell: ({ row }) => {
      return (
        <Square
          sx={{
            bgcolor: (theme) =>
              theme.palette.mode === "dark" ? "background.paper" : "#121212",
          }}
        >
          <img
            src={`/icons/roles/${row.original.role}.png`}
            width={16}
            height={16}
          />
        </Square>
      );
    },
  },
  {
    id: "level",
    header: SortableHeader("LVL"),
    accessorKey: "level",
    aggregationFn: "mean",
    cell: ({ row }) => {
      return (
        <LevelColored level={row.original.level}>
          {row.original.level}
        </LevelColored>
      );
    },
  },
  {
    id: "name",
    header: SortableHeader("Name"),
    accessorKey: "name",
    cell: ({ row }) => {
      return (
        <Box
          sx={{
            textOverflow: "ellipsis",
            overflow: "hidden",
            textWrap: "nowrap",
            width: "20ch",
          }}
        >
          <span>{row.original.name}</span>
        </Box>
      );
    },
  },
  {
    id: "country",
    header: SortableHeader("Country"),
    accessorKey: "country",
    cell: ({ row }) => {
      return row.original.country && row.original.country !== "private" ? (
        <CountryFlag country={row.original.country} />
      ) : null;
    },
  },
  {
    id: "vip",
    header: SortableHeader("VIP"),
    accessorKey: "is_vip",
    cell: ({ row }) => {
      return row.original.is_vip ? (
        <Star sx={{ fontSize: 12, color: yellow["500"] }} />
      ) : null;
    },
  },
  {
    id: "flags",
    header: "Flags",
    accessorKey: "profile.flags",
    cell: ({ row }) => {
      const flags = row.original.profile.flags;
      if (!flags || flags.length === 0) return null;
      const flagsCount = 2;
      return (
        <Stack spacing={0.25} direction={"row"} alignItems={"center"}>
          {flags.map(({ flag, comment: note, modified }) => (
            <Tooltip title={note} key={modified}>
              <Box>{flag}</Box>
            </Tooltip>
          ))}
          {flags.length - flagsCount > 0 ? (
            <Typography>{`+${flags.length - flagsCount}`}</Typography>
          ) : null}
        </Stack>
      );
    },
  },
  {
    id: "time",
    header: SortableHeader("Time"),
    accessorKey: "profile.current_playtime_seconds",
    aggregationFn: "mean",
    cell: ({ row }) => {
      return (
        <>
          {dayjs
            .duration(row.original.profile.current_playtime_seconds, "seconds")
            .format("H:mm")}
        </>
      );
    },
  },
  {
    id: "warnings",
    header: SortableHeader("⚠️"),
    accessorKey: "profile.received_actions",
    cell: ({ row }) => {
      return hasRecentWarnings(row.original.profile.received_actions) ? (
        <Warning sx={{ fontSize: 12, color: yellow["500"] }} />
      ) : null;
    },
  },
  {
    id: "actions",
    header: "🛠️",
    accessorKey: "actions",
    cell: ({ row }) => {
      return (
        <ActionMenuButton
          actions={playerGameActions}
          recipients={row.original}
          orientation="horizontal"
          disableRipple={true}
          sx={{
            width: 12,
            height: 12,
          }}
        />
      );
    },
  },
];
