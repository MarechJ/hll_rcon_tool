import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import dayjs from "dayjs";
import { Action, SortableHeader, TextButton } from "@/components/table/styles";
import { generatePlayerActions } from "@/features/player-action/actions";
import { LogMessage } from "@/components/shared/LogMessage";
import { getLogTeam, getTeamColor } from "@/utils/lib";
import { Box } from "@mui/material";
import { Stack } from "@mui/material";
import { blue, red } from "@mui/material/colors";
import CopyableText from "@/components/shared/CopyableText";

const TIME_FORMAT = "HH:mm:ss, MMM DD";

const PlayerNameWithId = ({ children, playerId }) => (
  <Stack sx={{ textAlign: "left" }}>
    {children}
    <CopyableText
      text={playerId}
      size="0.65em"
      sx={{
        fontSize: "0.65em",
        color: "text.secondary",
        '[data-expanded-view="false"] &': {
          display: "none",
        },
      }}
    />
  </Stack>
);

const playerNameFilter = (row, columnId, filterValue = []) => {
  // If no filter value, show all rows
  if (!filterValue.length) return true;

  const player1 = row.original.player_name_1;
  const player2 = row.original.player_name_2;

  // Check if either player name matches the filter value
  return filterValue.includes(player1) || filterValue.includes(player2);
};

const actionFilter = (row, columnId, filterValue = []) => {
  if (!filterValue) return true;
  const anyStartsWith = filterValue.some((action) => {
    switch (action) {
      case "CHAT":
      case "ADMIN":
      case "VOTE":
      case "MATCH":
        return row.original.action.startsWith(action);
      default:
        return row.original.action === action;
    }
  });
  return anyStartsWith;
};

const teamFilter = (row, columnId, filterValue = []) => {
  if (!filterValue.length) return true;
  const team = row.getValue(columnId);
  return filterValue.includes(team);
};

// Column definitions for the log table
export const logsColumns = [
  {
    header: SortableHeader("Time"),
    accessorKey: "timestamp_ms",
    cell: ({ row }) => {
      return dayjs(row.original.timestamp_ms).format(TIME_FORMAT);
    },
    meta: {
      variant: "time",
    },
  },
  {
    header: SortableHeader("Team"),
    id: "team",
    accessorFn: (log) => getLogTeam(log),
    filterFn: teamFilter,
    cell: ({ getValue, row }) => {
      const team = getValue();
      if (!team) return null;
      return (
        <Box
          sx={{
            backgroundColor: team === "Axis" ? red[400] : blue[400],
            textTransform: "uppercase",
            fontWeight: "bold",
            fontSize: "0.75em",
            color: "black",
            padding: "0.15em 0.25em",
            textAlign: "center",
          }}
        >
          {team}
        </Box>
      );
    },
    meta: {
      variant: "short",
    },
  },
  {
    header: "This Player",
    accessorKey: "player_name_1",
    cell: ({ row }) => {
      return row.original.player_name_1 && row.original.player_id_1 ? (
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: false,
            onlineAction: true,
          })}
          withProfile
          recipients={{
            player_id: row.original.player_id_1,
            name: row.original.player_name_1,
          }}
          renderButton={(props) => (
            <PlayerNameWithId playerId={row.original.player_id_1}>
              <TextButton {...props}>{row.original.player_name_1}</TextButton>
            </PlayerNameWithId>
          )}
        />
      ) : row.original.player_name_1 ? (
        <span>{row.original.player_name_1}</span>
      ) : null;
    },
    filterFn: playerNameFilter,
    meta: {
      variant: "action",
    },
  },
  {
    header: "This Player (Colored)",
    id: "player_name_1_colored",
    accessorFn: (log) => log.player_name_1,
    cell: ({ row }) => {
      const name = row.original.player_name_1;
      const playerId = row.original.player_id_1;
      const color = getTeamColor(getLogTeam(row.original));
      return name && playerId ? (
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: false,
            onlineAction: true,
          })}
          withProfile
          recipients={{ player_id: playerId, name }}
          renderButton={(props) => (
            <PlayerNameWithId playerId={playerId}>
              <TextButton {...props} sx={{ color }}>
                {name}
              </TextButton>
            </PlayerNameWithId>
          )}
        />
      ) : name ? (
        <Box component="span" sx={{ color }}>
          {name}
        </Box>
      ) : null;
    },
    filterFn: playerNameFilter,
    meta: { variant: "action" },
  },
  {
    header: "Action",
    accessorKey: "action",
    id: "action",
    cell: ({ row }) => {
      return <Action type={row.original.action}>{row.original.action}</Action>;
    },
    filterFn: actionFilter,
    meta: {
      variant: "action",
    },
  },
  {
    header: "That Player",
    accessorKey: "player_name_2",
    filterFn: playerNameFilter,
    cell: ({ row }) => {
      return row.original.player_name_2 && row.original.player_id_2 ? (
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: false,
            onlineAction: true,
          })}
          withProfile
          recipients={{
            player_id: row.original.player_id_2,
            name: row.original.player_name_2,
          }}
          renderButton={(props) => (
            <PlayerNameWithId playerId={row.original.player_id_2}>
              <TextButton {...props}>{row.original.player_name_2}</TextButton>
            </PlayerNameWithId>
          )}
        />
      ) : row.original.player_name_2 ? (
        <span>{row.original.player_name_2}</span>
      ) : null;
    },
    meta: {
      variant: "name",
    },
  },
  {
    header: "That Player (Colored)",
    id: "player_name_2_colored",
    accessorFn: (log) => log.player_name_2,
    filterFn: playerNameFilter,
    cell: ({ row }) => {
      const name = row.original.player_name_2;
      const playerId = row.original.player_id_2;
      const firstTeam = getLogTeam(row.original);
      const secondTeam =
        row.original.action === "TEAM KILL"
          ? firstTeam
          : firstTeam === "Axis"
          ? "Allies"
          : firstTeam === "Allies"
          ? "Axis"
          : undefined;
      const color = getTeamColor(secondTeam);
      return name && playerId ? (
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: false,
            onlineAction: true,
          })}
          withProfile
          recipients={{ player_id: playerId, name }}
          renderButton={(props) => (
            <PlayerNameWithId playerId={playerId}>
              <TextButton {...props} sx={{ color }}>
                {name}
              </TextButton>
            </PlayerNameWithId>
          )}
        />
      ) : name ? (
        <Box component="span" sx={{ color }}>
          {name}
        </Box>
      ) : null;
    },
    meta: { variant: "name" },
  },
  {
    header: "Message (Colored, No IDs)",
    id: "message_colored",
    accessorKey: "message",
    cell: ({ row }) => {
      return (
        <LogMessage log={row.original} colored={true} include_ids={false} />
      );
    },
  },
  {
    header: "Message",
    id: "message_with_id",
    accessorKey: "message",
    cell: ({ row }) => {
      return (
        <LogMessage log={row.original} colored={true} include_ids={true} />
      );
    },
  },
  {
    header: "Message",
    id: "message",
    accessorKey: "message",
    cell: ({ row }) => {
      return <LogMessage log={row.original} colored={false} />;
    },
  },
  {
    header: "Full Message",
    id: "full_message",
    accessorKey: "message",
    meta: {
      size: "full",
      variant: "content",
    },
  },
  {
    header: "Short Message",
    id: "short_message",
    accessorKey: "message",
    cell: ({ row }) => {
      return <LogMessage log={row.original} colored={false} short={true} />;
    },
  },
];
