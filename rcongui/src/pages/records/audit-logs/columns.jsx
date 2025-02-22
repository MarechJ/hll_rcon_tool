import CopyableText from "@/components/shared/CopyableText";
import { TextButton } from "@/components/table/styles";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import dayjs from "dayjs";

export const auditLogsColumns = [
  {
    header: "Time",
    accessorKey: "creation_time",
    cell: ({ row }) => {
      return dayjs(row.original.creation_time).format("lll");
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
    accessorKey: "command",
  },
  {
    header: "Player",
    cell: ({ row }) => {
      const { openWithId } = usePlayerSidebar();
      let args, player, playerId;
      try {
        args = JSON.parse(row.original.command_arguments);
        player = args.player_name ?? args.description;
        playerId = args.player_id;
      } catch (e) {
        return "";
      }
      
      if (playerId) {
        return (
          <TextButton
            onClick={(e) => {
              e.stopPropagation();
              openWithId(playerId);
            }}
          >
            {player}
          </TextButton>
        );
      }

      return player;
    },
  },
  {
    header: "Player ID",
    cell: ({ row }) => {
      let args, playerId;
      try {
        args = JSON.parse(row.original.command_arguments);
        playerId = args.player_id;
      } catch (e) {
        return "";
      }
      return <CopyableText text={playerId} />;
    },
  },
];
