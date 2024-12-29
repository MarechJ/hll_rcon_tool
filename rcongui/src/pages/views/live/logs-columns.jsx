import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import dayjs from "dayjs";
import { Action, SortableHeader, TextButton } from "@/components/table/styles";
import { generatePlayerActions } from "@/features/player-action/actions";

const TIME_FORMAT = "HH:mm:ss, MMM DD";

const removePlayerIds = (message) => {
  // Combine both regex patterns into one
  return message.replace(
    /\((?:(?:Axis|Allies)\/)?(?:[0-9]{17}|[A-Z0-9]{16})\)/g,
    ""
  );
};

const playerNameFilter = (row, columnId, filterValue = []) => {
  // If no filter value, show all rows
  if (!filterValue.length) return true;
  
  const player1 = row.original.player_name_1;
  const player2 = row.original.player_name_2;
  
  // Check if either player name matches the filter value
  return filterValue.includes(player1) || filterValue.includes(player2);
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
      variant: "time"
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
          recipients={{ player_id: row.original.player_id_1, name: row.original.player_name_1 }}
          renderButton={(props) => (
            <TextButton {...props}>{row.original.player_name_1}</TextButton>
          )}
        />
      ) : row.original.player_name_1 ? <span>{row.original.player_name_1}</span> : null;
    },
    filterFn: playerNameFilter,
    meta: {
      variant: "name"
    },
  },
  {
    header: "Action",
    accessorKey: "action",
    id: "action",
    cell: ({ row }) => {
      return <Action type={row.original.action}>{row.original.action}</Action>;
    },
    filterFn: "arrIncludesSome",
    meta: {
      variant: "action"
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
          recipients={{ player_id: row.original.player_id_2, name: row.original.player_name_2 }}
          renderButton={(props) => (
            <TextButton {...props}>{row.original.player_name_2}</TextButton>
          )}
        />
      ) : row.original.player_name_2 ? <span>{row.original.player_name_2}</span> : null;
    },
    meta: {
      variant: "name"
    },
  },
  {
    header: "Message",
    accessorKey: "message",
    meta: {
      size: "full",
      variant: "content",
    },
    cell: ({ row }) => {
      return removePlayerIds(row.original.message);
    },
  },
];
