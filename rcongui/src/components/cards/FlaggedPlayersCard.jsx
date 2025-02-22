import { useGlobalStore } from "@/stores/global-state";
import { useMemo } from "react";
import OnlineUsersCard from "@/components/shared/card/UsersCard";
import { Stack, Typography } from "@mui/material";
import Emoji from "@/components/shared/Emoji";

const FlaggedPlayersCard = () => {
  const onlinePlayers = useGlobalStore((state) => state.onlinePlayers);

  const playersGroupedByFlags = useMemo(() => {
    return Object.entries(
      onlinePlayers.reduce((acc, player) => {
        const flags = player.profile?.flags?.map((flag) => flag.flag);
        flags.forEach((flag) => {
          acc[flag] = (acc[flag] || []).concat({
            id: player.player_id,
            name: player.name,
            avatar: player.profile?.steaminfo?.profile?.avatar,
          });
        });
        return acc;
      }, {})
    ).map(([flag, players]) => ({
      group: flag,
      label: <Stack direction={"row"} alignItems={"center"} spacing={0.5}>
        <Emoji emoji={flag} size={16} />
        <Typography variant="subtitle2">({players.length})</Typography>
      </Stack>,
      users: players,
    }));
  }, [onlinePlayers]);

  return (
    <OnlineUsersCard 
      title="Flagged" 
      onlineUsers={playersGroupedByFlags} 
    />
  );
};

export default FlaggedPlayersCard; 