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
  
  const player1 = row.original.player1_name;
  const player2 = row.original.player2_name;
  
  // Check if either player name matches the filter value
  return filterValue.includes(player1) || filterValue.includes(player2);
};

// Column definitions for the log table
export const logsColumns = [
  {
    header: SortableHeader("Time"),
    accessorKey: "event_time",
    cell: ({ row }) => {
      return dayjs.utc(row.original.event_time).tz(Intl.DateTimeFormat().resolvedOptions().timeZone).format(TIME_FORMAT);
    },
    meta: {
      variant: "time"
    },
  },
  {
    header: "This Player",
    accessorKey: "player1_name",
    cell: ({ row }) => {
      return row.original.player1_name && row.original.player1_id ? (
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: false,
            onlineAction: true,
          })}
          withProfile
          recipients={{ player_id: row.original.player1_id, name: row.original.player1_name }}
          renderButton={(props) => (
            <TextButton {...props}>{row.original.player1_name}</TextButton>
          )}
        />
      ) : row.original.player1_name ? <span>{row.original.player1_name}</span> : null;
    },
    filterFn: playerNameFilter,
    meta: {
      variant: "name"
    },
  },
  {
    header: "Action",
    accessorKey: "type",
    id: "type",
    cell: ({ row }) => {
      return <Action type={row.original.type}>{row.original.type}</Action>;
    },
    filterFn: "arrIncludesSome",
    meta: {
      variant: "action"
    },
  },
  {
    header: "That Player",
    accessorKey: "player2_name",
    filterFn: playerNameFilter,
    cell: ({ row }) => {
      return row.original.player2_name && row.original.player2_id ? (
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: false,
          })}
          withProfile
          recipients={{ player_id: row.original.player2_id, name: row.original.player2_name }}
          renderButton={(props) => (
            <TextButton {...props}>{row.original.player2_name}</TextButton>
          )}
        />
      ) : row.original.player2_name ? <span>{row.original.player2_name}</span> : null;
    },
    meta: {
      variant: "name"
    },
  },
  {
    header: "Message",
    accessorKey: "content",
    meta: {
      size: "full",
      variant: "content",
    },
    cell: ({ row }) => {
      return removePlayerIds(row.original.content);
    },
  },
];
