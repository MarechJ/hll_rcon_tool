import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { playerGameActions } from "@/features/player-action/actions";
import { Button } from "@mui/material";
import { styled } from "@mui/material/styles";
import dayjs from "dayjs";
import { Action, SortableHeader, TextButton } from "@/components/table/styles";

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

const getLogSeverity = (log) => {
  switch (log.action) {
    case "TEAM KILL":
    case "TK AUTO":
    case "TK AUTO BANNED":
    case "TK AUTO KICKED":
    case "ADMIN KICKED":
    case "ADMIN BANNED":
      return "warning";
    case "ADMIN MISC":
    case "CAMERA":
    case "VOTE COMPLETED":
    case "MESSAGE":
      return "info";
    case "CHAT":
    case "CHAT[Allies]":
    case "CHAT[Allies][Team]":
    case "CHAT[Allies][Unit]":
    case "CHAT[Axis]":
    case "CHAT[Axis][Team]":
    case "CHAT[Axis][Unit]":
      return "chat";
    default:
      return "normal";
  }
};

/*
 Log example: 
    {
        "version": 1,
        "timestamp_ms": 1729630418000,
        "event_time": "2024-10-22T20:53:38",
        "relative_time_ms": -1632.637,
        "raw": "[1.10 sec (1729630418)] DISCONNECTED HereCookie76152 (e520836e51d683d06f56e06e4cb74118)",
        "line_without_time": "DISCONNECTED HereCookie76152 (e520836e51d683d06f56e06e4cb74118)",
        "action": "DISCONNECTED",
        "player_name_1": "HereCookie76152",
        "player_id_1": "e520836e51d683d06f56e06e4cb74118",
        "player_name_2": null,
        "player_id_2": null,
        "weapon": null,
        "message": "HereCookie76152 (e520836e51d683d06f56e06e4cb74118)",
        "sub_content": null
    }

    or

    {
        "version": 1,
        "timestamp_ms": 1729629560000,
        "event_time": "2024-10-22T20:39:20",
        "relative_time_ms": -1363.4550000000002,
        "raw": "[1.00 sec (1729629560)] TEAM KILL: blanquartmael(Axis/76561199409157448) -> PeaceUndead(Axis/6d7e77a018bc9213cb1045ea67324367) with WALTHER P38",
        "line_without_time": "TEAM KILL: blanquartmael(Axis/76561199409157448) -> PeaceUndead(Axis/6d7e77a018bc9213cb1045ea67324367) with WALTHER P38",
        "action": "TEAM KILL",
        "player_name_1": "blanquartmael",
        "player_id_1": "76561199409157448",
        "player_name_2": "PeaceUndead",
        "player_id_2": "6d7e77a018bc9213cb1045ea67324367",
        "weapon": "WALTHER P38",
        "message": "blanquartmael(Axis/76561199409157448) -> PeaceUndead(Axis/6d7e77a018bc9213cb1045ea67324367) with WALTHER P38",
        "sub_content": null
    }
*/

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
      return row.original.player_name_1 ? (
        <ActionMenuButton
          actions={playerGameActions}
          withProfile
          recipients={{ player_id: row.original.player_id_1, name: row.original.player_name_1 }}
          renderButton={(props) => (
            <TextButton {...props}>{row.original.player_name_1}</TextButton>
          )}
        />
      ) : null;
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
      return row.original.player_name_2 ? (
        <ActionMenuButton
          actions={playerGameActions}
          withProfile
          recipients={{ player_id: row.original.player_id_2, name: row.original.player_name_2 }}
          renderButton={(props) => (
            <TextButton {...props}>{row.original.player_name_2}</TextButton>
          )}
        />
      ) : null;
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
    },
    cell: ({ row }) => {
      return removePlayerIds(row.original.message);
    },
  },
];
