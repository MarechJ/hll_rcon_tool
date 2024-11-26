import React from "react";
import {
  Box,
  Checkbox,
  IconButton,
  Stack,
  styled,
  Tooltip,
  Typography,
} from "@mui/material";
import { Star, Warning } from "@mui/icons-material";
import { yellow } from "@mui/material/colors";
import dayjs from "dayjs";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";
import { CountryFlag } from "@/components/shared/CountryFlag";
import {
  getPlayerTier,
  hasRecentWarnings,
  teamToNation,
  tierColors,
} from "@/utils/lib";
import { SortableHeader } from "@/components/table/styles";
import RemoveRedEyeIcon from "@mui/icons-material/RemoveRedEye";
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

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
    accessorKey: "team",
    id: "team",
    header: SortableHeader("T"),
    cell: ({ row }) => {
      return (
        <Center>
          <Square>
            <img
              src={`/icons/teams/${teamToNation(row.original.team)}.webp`}
              width={16}
              height={16}
            />
          </Square>
        </Center>
      );
    },
    meta: {
      variant: "icon",
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
        <>
          <Center>
            <Square>
              {row.original.unit_name?.toUpperCase() ?? "-"}
            </Square>
          </Center>
        </>
      );
    },
    meta: {
      variant: "short",
    },
  },
  {
    id: "role",
    header: SortableHeader("R"),
    accessorKey: "role",
    cell: ({ row }) => {
      const src = row.getCanExpand() ? `/icons/roles/${row.original.type ?? row.original.role}.png` : `/icons/roles/${row.original.role}.png`;

      return row.team !== "neutral" ? (
            <Center>
              <Square
                sx={{
                  bgcolor: (theme) =>
                    theme.palette.mode === "dark" ? "background.paper" : "#121212",
                }}
              >
                <img
                  src={src}
                  width={16}
                  height={16}
                />
              </Square>
            </Center>
      ) : null;
    },
    meta: {
      variant: "icon",
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
    meta: {
      variant: "short",
    },
  },
  {
    id: "actions",
    header: "🛠️",
    accessorKey: "actions",
    cell: ({ row }) => {
      if (row.getCanExpand()) return (
        <IconButton
          size="small"
          sx={{ p: 0, width: 16, height: 16, fontSize: 12 }}
          onClick={row.getToggleExpandedHandler()}
        >
          {row.getIsExpanded() ? <ExpandMoreIcon /> : <ChevronRightIcon />}
        </IconButton>
      );

      return (
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: false,
            onlineAction: true,
          })}
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
    meta: {
      variant: "icon",
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
    id: "kills",
    header: SortableHeader("K"),
    accessorKey: "kills",
    aggregationFn: "sum",
    cell: ({ row }) => {
      return (
        <>
          {row.original.kills}
        </>
      );
    },
    meta: {
      variant: "short",
    },
  },
  {
    id: "deaths",
    header: SortableHeader("D"),
    accessorKey: "deaths",
    aggregationFn: "sum",
    cell: ({ row }) => {
      return (
        <>
          {row.original.deaths}
        </>
      );
    },
    meta: {
      variant: "short",
    },
  },
  {
    id: "combat",
    header: SortableHeader("C"),
    accessorKey: "combat",
    aggregationFn: "sum",
    cell: ({ row }) => {
      return (
        <>
          {row.original.combat}
        </>
      );
    },
    meta: {
      variant: "short",
    },
  },
  {
    id: "offense",
    header: SortableHeader("O"),
    accessorKey: "offense",
    aggregationFn: "sum",
    cell: ({ row }) => {
      return (
        <>
          {row.original.offense}
        </>
      );
    },
    meta: {
      variant: "short",
    },
  },
  {
    id: "defense",
    header: SortableHeader("D"),
    accessorKey: "defense",
    aggregationFn: "sum",
    cell: ({ row }) => {
      return (
        <>
          {row.original.defense}
        </>
      );
    },
    meta: {
      variant: "short",
    },
  },
  {
    id: "support",
    header: SortableHeader("S"),
    accessorKey: "support",
    aggregationFn: "sum",
    cell: ({ row }) => {
      return (
        <>
          {row.original.support}
        </>
      );
    },
    meta: {
      variant: "short",
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
    meta: {
      variant: "short",
    },
  },
];
