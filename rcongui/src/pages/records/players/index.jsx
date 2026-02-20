import { cmd } from "@/utils/fetchUtils";
import {
  Button,
  Stack,
  Grid2 as Grid,
  Typography,
  Divider,
} from "@mui/material";
import {
  useLoaderData,
  useNavigation,
} from "react-router-dom";
import { useMemo, useState, memo, useCallback, useEffect } from "react";
import PlayerCard from "@/components/shared/card/PlayerCard";
import NavPagination from "@/pages/stats/games/nav-pagination";
import { Box } from "@mui/material";
import { useGlobalStore } from "@/stores/global-state";
import { ActionBar } from "@/features/player-action/ActionMenu";
import { newRecordActions } from "@/features/player-action/actions";
import PlayerFiltersForm from "./PlayerFiltersForm";

// Create a memoized version of PlayerCard
const MemoizedPlayerCard = memo(PlayerCard);

// Create a separate component for the players section
const PlayersGrid = memo(
  ({ players, selectedIds, handlePlayerSelect, ...props }) => {
    return (
      <Grid container spacing={1} {...props}>
        {players.map((player) => (
          <Grid
            key={player.player_id}
            size={{ xs: 12, sm: 6, md: "auto" }}
          >
            <MemoizedPlayerCard
              player={player}
              selected={selectedIds.has(player.player_id)}
              onSelect={handlePlayerSelect}
            />
          </Grid>
        ))}
      </Grid>
    );
  }
);

export const loader = async ({ request }) => {
  const url = new URL(request.url);

  const player_name = url.searchParams.get("player_name") ?? "";
  const player_id = url.searchParams.get("player_id") ?? "";

  const last_seen_from = url.searchParams.get("last_seen_from") ?? "";
  const last_seen_till = url.searchParams.get("last_seen_till") ?? "";

  const page = url.searchParams.get("page")
    ? Number(url.searchParams.get("page"))
    : 1;
  const page_size = url.searchParams.get("page_size")
    ? Number(url.searchParams.get("page_size"))
    : 50;

  const flags = url.searchParams.get("flags")
    ? url.searchParams.get("flags").split(",")
    : [];
  const country = url.searchParams.get("country") ?? "";

  const blacklisted = url.searchParams.get("blacklisted") ?? false;
  const exact_name_match = url.searchParams.get("exact_name_match") ?? false;
  const ignore_accent = url.searchParams.get("ignore_accent") ?? false;
  const is_watched = url.searchParams.get("is_watched") ?? false;

  const fields = {
    player_id,
    page,
    page_size,
    flags,
    blacklisted,
    exact_name_match,
    ignore_accent,
    is_watched,
    player_name,
    country,
    last_seen_from,
    last_seen_till,
  };

  // In the background, this command is POST request therefore the payload and not params
  const playersRecords = await cmd.GET_PLAYERS_RECORDS({
    payload: Object.fromEntries(
      Object.entries(fields).filter(
        ([_, value]) => value !== "" && value !== null
      )
    ),
  });

  const bans = await cmd.GET_BANS();

  return {
    players: playersRecords.result.players.map((player) => ({
      ...player,
      is_banned: bans.some((ban) => ban.player_id === player.player_id),
    })),
    total_pages:
      page_size > 0
        ? Math.ceil(Number(playersRecords.result.total) / page_size)
        : 1,
    page: Number(page),
    fields,
  };
};

export default function PlayersRecords() {
  const { players: playersData, fields, total_pages, page } = useLoaderData();
  const navigation = useNavigation();
  const server = useGlobalStore((state) => state.serverState);
  const onlinePlayers = useGlobalStore((state) => state.onlinePlayers);
  const [selectedPlayerIds, setSelectedPlayerIds] = useState(new Set());
  // Cache player data by player_id to support multi-page selection
  const [playerCache, setPlayerCache] = useState(new Map());

  const players = useMemo(() => {
    if (!server) return playersData;
    return playersData.map((player) => {
      const thisOnlinePlayer = onlinePlayers.find(
        (aPlayer) => aPlayer.player_id === player.player_id
      );

      const profile = {
        ...player,
        is_online: false,
        is_vip:
          player.vips &&
          player.vips.some((vip) => vip.server_number === server.server_number),
      };

      if (thisOnlinePlayer) {
        profile.is_online = true;
        profile.level = thisOnlinePlayer.level || player.soldier.level;
        profile.clan_tag = thisOnlinePlayer.clan_tag || player.soldier.clan_tag;
        profile.platform = thisOnlinePlayer.platform || player.soldier.platform;
      }

      return profile;
    });
  }, [playersData, server, onlinePlayers]);

  // Update cache with current page players
  useEffect(() => {
    setPlayerCache((prevCache) => {
      const newCache = new Map(prevCache);
      for (const player of players) {
        newCache.set(player.player_id, player);
      }
      return newCache;
    });
  }, [players]);

  const handlePlayerSelect = useCallback((player) => {
    setSelectedPlayerIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(player.player_id)) {
        newSet.delete(player.player_id);
      } else {
        newSet.add(player.player_id);
      }
      return newSet;
    });
  }, []);

  const handleSelectAllPlayers = useCallback(() => {
    setSelectedPlayerIds((prev) => {
      // Check if all current page players are already selected
      const currentPageIds = new Set(players.map((p) => p.player_id));
      const allCurrentPageSelected = players.every((p) => prev.has(p.player_id));
      
      if (allCurrentPageSelected && players.length > 0) {
        // All current page players are selected, return unchanged
        return prev;
      }
      
      // Add all current page players to existing selection
      const newSet = new Set(prev);
      for (const player of players) {
        newSet.add(player.player_id);
      }
      return newSet;
    });
  }, [players]);

  const handleUnselectAllPlayers = () => {
    setSelectedPlayerIds(new Set())
  }

  // Convert Set to array of player objects for ActionBar
  // Uses cache to include players from all pages, not just current page
  const selectedPlayers = useMemo(() => {
    const result = [];
    for (const playerId of selectedPlayerIds) {
      const cachedPlayer = playerCache.get(playerId);
      if (cachedPlayer) {
        // Ensure the player has a name field for ActionForm
        const playerName = 
          cachedPlayer.name ??
          cachedPlayer.account?.name ??
          cachedPlayer.names?.[0]?.name ??
          cachedPlayer.soldier?.name ??
          playerId;
        
        result.push({
          ...cachedPlayer,
          name: playerName,
          player_name: playerName, // Explicitly set player_name for actions
        });
      } else {
        // Fallback: create minimal player object if not in cache
        // This shouldn't happen often, but handles edge cases
        result.push({
          player_id: playerId,
          player_name: playerId,
          name: playerId,
          names: [{ name: playerId }],
        });
      }
    }
    return result;
  }, [selectedPlayerIds, playerCache]);

  return (
    <Stack spacing={1} sx={{ mt: 2 }}>
      <ActionBar actions={newRecordActions} recipients={selectedPlayers} />
      <Stack direction={{ xs: "column", lg: "row" }} spacing={1} sx={{ mt: 2 }}>
        {/* FILTERS */}
        <PlayerFiltersForm fields={fields} />
        {/* MAIN CONTENT */}
        <Stack
          component="section"
          id="players-section"
          spacing={1}
          sx={{ width: "100%" }}
        >
          <Stack direction={"row"} spacing={1} alignItems={"center"}>
            <Typography>Selected: {selectedPlayerIds.size}</Typography>
            <Button size="small" variant="outlined" onClick={handleSelectAllPlayers}>Select All</Button>
            <Button size="small" variant="outlined" onClick={handleUnselectAllPlayers}>Unselect All</Button>
            <Divider flexItem orientation="vertical" />
            <NavPagination
              page={page}
              maxPages={total_pages}
              disabled={navigation.state === "loading"}
            />
          </Stack>
          <PlayersGrid
            players={players}
            selectedIds={selectedPlayerIds}
            handlePlayerSelect={handlePlayerSelect}
          />
          <Box sx={{ flexGrow: 1 }} />
          <NavPagination
            page={page}
            maxPages={total_pages}
            disabled={navigation.state === "loading"}
          />
        </Stack>
      </Stack>
    </Stack>
  );
}
