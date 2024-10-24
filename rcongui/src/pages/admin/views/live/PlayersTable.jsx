import React, { useState } from "react";
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import { NoRowsOverlay } from "@/components/NoRowsOverlay";
import { CountryFlag } from "@/components/CountryFlag";
import {
  Box,
  Stack,
  styled,
  Tooltip,
  Typography,
} from "@mui/material";
import { Star, Warning } from "@mui/icons-material";
import { blue, green, purple, red, yellow } from "@mui/material/colors";
import dayjs from "dayjs";
import { ActionMenu } from "@/features/player-action/ActionMenu";
import { playerGameActions } from "@/features/player-action/actions";
import { useActionDialog } from "@/hooks/useActionDialog";

// player example
/* 
{
    "name": "JaCuTab",
    "player_id": "76561198004399730",
    "country": null,
    "steam_bans": {
        "SteamId": "76561198004399730",
        "VACBanned": false,
        "EconomyBan": "none",
        "CommunityBanned": false,
        "NumberOfVACBans": 0,
        "DaysSinceLastBan": 0,
        "NumberOfGameBans": 0
    },
    "profile": {
        "id": 49,
        "player_id": "76561198004399730",
        "created": "2022-08-14T17:20:04.324",
        "names": [
            {
                "id": 49,
                "name": "[VLK] Spifly",
                "player_id": "76561198004399730",
                "created": "2022-08-14T17:20:04.338",
                "last_seen": "2024-04-05T17:27:17"
            }
        ],
        "sessions": [
            {
                "id": 56620,
                "player_id": "76561198004399730",
                "start": "2024-04-05T17:27:17",
                "end": null,
                "created": "2024-04-05T17:27:59.605"
            }
        ],
        "sessions_count": 299,
        "total_playtime_seconds": 1480666,
        "current_playtime_seconds": 2542,
        "received_actions": [
            {
                "action_type": "PUNISH",
                "reason": "You violated seeding rules on this server: Attacking 4th cap while seeding is not allowed.\nYou're being punished by a bot (1/-1).\nNext check in 30 seconds",
                "by": "SeedingRulesAutomod",
                "time": "2024-03-02T21:30:26.257"
            },
            {
                "action_type": "PUNISH",
                "reason": "You violated seeding rules on this server: Attacking 4th cap while seeding is not allowed.\nYou're being punished by a bot (1/-1).\nNext check in 30 seconds",
                "by": "SeedingRulesAutomod",
                "time": "2024-03-01T21:48:00.909"
            },
            {
                "action_type": "PUNISH",
                "reason": "You violated seeding rules on this server: Attacking 4th cap while seeding is not allowed.\nYou're being punished by a bot (1/-1).\nNext check in 30 seconds",
                "by": "SeedingRulesAutomod",
                "time": "2024-02-20T22:20:02.773"
            },
            {
                "action_type": "PUNISH",
                "reason": "You violated seeding rules on this server: Attacking 4th cap while seeding is not allowed.\nYou're being punished by a bot (1/-1).\nNext check in 30 seconds",
                "by": "SeedingRulesAutomod",
                "time": "2024-01-24T21:46:55.567"
            }
        ],
        "penalty_count": {
            "KICK": 0,
            "PUNISH": 4,
            "TEMPBAN": 0,
            "PERMABAN": 0
        },
        "blacklist": null,
        "flags": [],
        "watchlist": { "is_watched": true },
        "steaminfo": {},
            "country": null,
            "bans": {
                "SteamId": "76561198004399730",
                "VACBanned": false,
                "EconomyBan": "none",
                "CommunityBanned": false,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 0,
                "NumberOfGameBans": 0
            },
            "has_bans": false
        },
        "vips": [
            {
                "server_number": 1,
                "expiration": "3000-01-01T00:00:00Z"
            }
        ]
    },
    "is_vip": true,
    "unit_id": 3,
    "unit_name": "dog",
    "loadout": "standard issue",
    "team": "axis",
    "role": "officer",
    "kills": 0,
    "deaths": 1,
    "combat": 0,
    "offense": 0,
    "defense": 40,
    "support": 0,
    "level": 318
},
*/

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
  const warnings = received_actions.filter((action) => action.time > warningsFrom);
  return warnings.length > 0;
}

const tierColors = {
  Novice: red[500],
  Apprentice: yellow[500],
  Expert: green[500],
  Master: blue[500],
  Legend: purple[500],
};

const Center = styled(Box)(({ theme }) => ({
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

// ... keep playerToRow function as is ...
export const columns = [
  {
    header: "T",
    accessorKey: "team",
    cell: ({ row }) => {
      return (
        <Center>
          <img
            src={`/icons/teams/${
              row.original.team === "axis" ? "ger" : "us"
            }.webp`}
            width={16}
            height={16}
          />
        </Center>
      );
    },
  },
  {
    header: "U",
    accessorKey: "unit_name",
    cell: ({ row }) => {
      return (
        <Center>
          {row.original.unit_name?.charAt(0)?.toUpperCase() ?? "-"}
        </Center>
      );
    },
  },
  {
    header: "R",
    accessorKey: "role",
    cell: ({ row }) => {
      return (
        <Center
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
        </Center>
      );
    },
  },
  {
    header: "Level",
    accessorKey: "level",
    cell: ({ row }) => {
      return (
        <LevelColored level={row.original.level}>
          {row.original.level}
        </LevelColored>
      );
    },
  },
  {
    header: "Name",
    accessorKey: "name",
    cell: ({ row }) => {
      return (
        <Box
          sx={{
            textOverflow: "ellipsis",
            overflow: "hidden",
            textWrap: "nowrap",
            maxWidth: "20ch",
          }}
        >
          {row.original.name}
        </Box>
      );
    },
  },
  {
    header: "Country",
    accessorKey: "country",
    cell: ({ row }) => {
      return row.original.country && row.original.country !== "private" ? (
        <CountryFlag country={row.original.country} />
      ) : null;
    },
  },
  {
    header: "VIP",
    accessorKey: "is_vip",
    cell: ({ row }) => {
      return row.original.is_vip ? (
        <Star sx={{ fontSize: 12, color: yellow["500"] }} />
      ) : null;
    },
  },
  {
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
    header: "Time",
    accessorKey: "profile.current_playtime_seconds",
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
    header: "⚠️",
    accessorKey: "profile.received_actions",
    cell: ({ row }) => {
      return hasRecentWarnings(row.original.profile.received_actions) ? (
        <Warning sx={{ fontSize: 12, color: yellow["500"] }} />
      ) : null;
    },
  },
  {
    header: "🛠️",
    accessorKey: "actions",
    cell: ({ row }) => {
      const { openDialog } = useActionDialog();
      return (
        <ActionMenu
          handleActionClick={(action) =>
            openDialog(action, [row.original.player_id])
          }
          actionList={playerGameActions}
          orientation="horizontal"
          size="small"
          sx={{
            width: 14,
            height: 14,
          }}
        />
      );
    },
  },
];

// The table will have a prop size ["small", "default", "large"]
// Styles will be different based on the size property
// The property size won't be passed to the component, but rather it will be used in the styled component
const StyledTable = styled("table", {
  shouldForwardProp: (prop) => prop !== "size",
})((styledProps) => {
  const theme = styledProps.theme;
  const size = styledProps.size ?? "default";
  return {
    fontSize: size === "small" ? 12 : size === "large" ? 16 : 14,
    borderCollapse: "collapse",
    borderSpacing: 0,
    border: `1px solid ${theme.palette.divider}`,
  };
});

const StyledTd = styled("td")(({ theme }) => ({
  padding: "1px 4px",
}));

const StyledTh = styled("th")(({ theme }) => ({
  padding: "1px 4px",
}));

const StyledTr = styled("tr")(({ theme }) => ({
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const PlayersTable = ({ data, columns }) => {
  const { openWithId, switchPlayer } = usePlayerSidebar();

  const [sorting, setSorting] = useState([]);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    getCoreRowModel: getCoreRowModel(),
    state: {
      sorting,
    },
  });

  return (
    <div>
      <StyledTable size={"small"}>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <StyledTr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <StyledTh
                  key={header.id}
                  onClick={header.column.getToggleSortingHandler()}
                >
                  {header.isPlaceholder ? null : (
                    <div>
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                    </div>
                  )}
                </StyledTh>
              ))}
            </StyledTr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <StyledTr
              key={row.id}
              onDoubleClick={() => openWithId(row.original.player_id)}
              onClick={() => switchPlayer(row.original.player_id)}
            >
              {row.getVisibleCells().map((cell) => (
                <StyledTd key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </StyledTd>
              ))}
            </StyledTr>
          ))}
        </tbody>
      </StyledTable>
      {table.getRowModel().rows.length === 0 && <NoRowsOverlay />}
    </div>
  );
};

export default PlayersTable;
