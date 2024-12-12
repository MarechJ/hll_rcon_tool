import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import dayjs from "dayjs";
import { Action, SortableHeader, TextButton } from "@/components/table/styles";
import { generatePlayerActions } from "@/features/player-action/actions";

const TIME_FORMAT = "HH:mm:ss, MMM DD";

const getTeamForLog = (log) => {
  let team;

  switch (log.action) {
    case "KILL":
    case "TEAM KILL":
      team = log.message.match(/\((?<team>Allies|Axis)\//)?.groups?.team;
      break;
    case "TEAMSWITCH":
      team = log.message.match(/>\D(?<team>Allies|Axis)/)?.groups?.team;
      break;
    case "CHAT":
    case "CHAT[Allies]":
    case "CHAT[Allies][Team]":
    case "CHAT[Allies][Unit]":
    case "CHAT[Axis]":
    case "CHAT[Axis][Team]":
    case "CHAT[Axis][Unit]":
      team = log.action.match(/(?<team>Allies|Axis)/)?.groups?.team;
      break;
    default:
      team = "Unknown";
      break;
  }

  return team ?? "Unknown";
};

const removePlayerIds = (message) => {
  // Combine both regex patterns into one
  return message.replace(
    /\((?:(?:Axis|Allies)\/)?(?:[0-9]{17}|[A-Z0-9]{16})\)/g,
    ""
  );
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
    filterFn: "arrIncludesSome",
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
