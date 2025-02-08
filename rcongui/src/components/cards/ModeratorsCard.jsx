import { useGlobalStore } from "@/hooks/useGlobalState";
import { useMemo } from "react";
import OnlineUsersCard from "@/components/shared/card/UsersCard";

const ModeratorsCard = () => {
  const onlinePlayers = useGlobalStore((state) => state.onlinePlayers);
  const onlineCrconMods = useGlobalStore((state) => state.onlineCrconMods);
  const onlineIngameMods = useGlobalStore((state) => state.onlineIngameMods);

  const ingameMods = useMemo(
    () =>
      onlineIngameMods.map((mod) => ({
        id: mod.id,
        name: mod.username,
        avatar: onlinePlayers.find(
          (player) => player.player_id === mod.player_id
        )?.profile?.steaminfo?.profile?.avatar,
      })),
    [onlineIngameMods, onlinePlayers]
  );

  const crconMods = useMemo(
    () =>
      onlineCrconMods.map((mod) => ({
        id: mod.id,
        name: mod.username,
        avatar: onlinePlayers.find(
          (player) => player.player_id === mod.player_id
        )?.profile?.steaminfo?.profile?.avatar,
      })),
    [onlineCrconMods, onlinePlayers]
  );

  return (
    <OnlineUsersCard
      title="Moderators"
      onlineUsers={[
        { group: "CRCON", label: `CRCON (${crconMods.length})`, users: crconMods, manageLink: "/admin" },
        {
          group: "In-Game",
          label: `In-Game (${ingameMods.length})`,
          users: ingameMods,
          manageLink: "/settings/console-admins",
        },
      ]}
    />
  );
};

export default ModeratorsCard; 