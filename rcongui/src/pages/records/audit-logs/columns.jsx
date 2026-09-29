import { TextButton } from "@/components/table/styles";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import dayjs from "dayjs";
import { auditDetails } from "./parse";

export const auditLogsColumns = [
  {
    header: "Time",
    accessorKey: "creation_time",
    cell: ({ row }) => {
      return dayjs(row.original.creation_time).format("MMM D, YYYY h:mm:ss A");
    },
    meta: {
      variant: "action",
    },
  },
  {
    header: "User",
    accessorKey: "username",
  },
  {
    header: "Action",
    cell: ({ row }) => {
      const { listName, listId } = auditDetails(row.original);
      const list = listName ?? (listId != null ? `#${listId}` : null);
      return (
        <>
          {row.original.command}
          {list && <span style={{ opacity: 0.7 }}> · {list}</span>}
        </>
      );
    },
  },
  {
    header: "Status",
    cell: ({ row }) => {
      const { failed, error } = auditDetails(row.original);
      return (
        <span title={error ?? undefined}>{failed ? "Failed" : "Success"}</span>
      );
    },
  },
  {
    header: "Player",
    cell: ({ row }) => {
      const { openWithId } = usePlayerSidebar();
      const { playerName: player, playerId } = auditDetails(row.original);

      if (playerId) {
        return (
          <TextButton
            onClick={(e) => {
              e.stopPropagation();
              openWithId(playerId);
            }}
          >
            {player ?? playerId}
          </TextButton>
        );
      }

      return player;
    },
  },
];
