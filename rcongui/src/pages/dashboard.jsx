import { useGlobalStore } from "@/hooks/useGlobalState";
import { cmd } from "@/utils/fetchUtils";
import {
  List,
  Card,
  ListItem,
  CardHeader,
  CardContent,
  styled,
  Box,
  Typography,
  Divider,
  Stack,
  Tooltip,
  IconButton,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import { Link } from "react-router-dom";
import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { LineChart } from "@mui/x-charts";
import dayjs from "dayjs";
import OnlineUsersCard from "@/components/shared/card/UsersCard";
import LogsCard from "@/components/shared/card/LogsCard";
import ScrollableCard from "@/components/shared/card/ScrollableCard";
import { MapAvatar } from "@/components/MapManager/map-details";
import Emoji from "@/components/shared/Emoji";
import SettingsIcon from '@mui/icons-material/Settings';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import ErrorIcon from '@mui/icons-material/Error';
import BlockIcon from '@mui/icons-material/Block';
import InfoIcon from '@mui/icons-material/Info';
import ServerSettingsCard from "@/components/cards/ServerSettingsCard";
import ServicesCard from "@/components/cards/ServicesCard";
import MapRotationCard from "@/components/cards/MapRotationCard";
import VIPWatchedCard from "@/components/cards/VIPWatchedCard";
import FlaggedPlayersCard from "@/components/cards/FlaggedPlayersCard";
import ModeratorsCard from "@/components/cards/ModeratorsCard";
import GamesCard from "@/components/cards/GamesCard";
import MapStatsCard from "@/components/cards/MapStatsCard";
import AutomodsCard from "@/components/cards/AutomodsCard";

const SMALL_CARD_SIZE = {
  xs: 12,
  sm: 6,
  xl: 3,
};

const MEDIUM_CARD_SIZE = {
  xs: 12,
  md: 6,
};

const LARGE_CARD_SIZE = {
  xs: 12,
};

const Dashboard = () => {
  const status = useGlobalStore((state) => state.status);

  const { data: logs = [] } = useQuery({
    queryKey: ["logs", "dashboard"],
    queryFn: async () => {
      const rawLogs = await cmd.GET_LIVE_LOGS({
        payload: {
          end: 15000,
          filter_action: [],
          filter_player: [],
          inclusive_filter: true,
        },
      });

      const logs = Object.entries(
        rawLogs.result.logs.reduce((acc, log) => {
          acc[log.action] = (acc[log.action] || []).concat(log);
          return acc;
        }, {})
      ).map(([action, logs]) => ({
        group: action,
        logs: logs.slice(0, 100).map((log) => ({
          user_1: {
            id: log.player_id_1,
            name: log.player_name_1,
          },
          user_2: {
            id: log.player_id_2,
            name: log.player_name_2,
          },
          message: log.message,
          timestamp: log.timestamp_ms,
          action: log.action,
        })),
      }));

      const adminLogs = rawLogs.result.logs
        .filter(
          (log) =>
            log.action.startsWith("CHAT") && log.message.includes("!admin")
        )
        .map((log) => ({
          user_1: {
            id: log.player_id_1,
            name: log.player_name_1,
          },
          user_2: {
            id: log.player_id_2,
            name: log.player_name_2,
          },
          message: log.message,
          timestamp: log.timestamp_ms,
          action: log.action,
        }));

      logs.push({
        group: "ADMIN",
        label: `Admin (${adminLogs.length})`,
        logs: adminLogs,
      });

      return logs;
    },
  });

  const { data: games = [] } = useQuery({
    queryKey: ["games", "dashboard"],
    enabled: status !== null,
    queryFn: async () => {
      const result = await cmd.GET_COMPLETED_GAMES({
        params: { page: 1, limit: 100 },
      });
      if (!result?.maps) return [];

      return result.maps
        .filter((game) => game.server_number === status.server_number)
        .slice(0, 15);
    },
  });


  return (
    <Grid container sx={{ overflow: "hidden" }} spacing={2}>
      <Grid size={SMALL_CARD_SIZE}>
        <ServerSettingsCard />
      </Grid>

      <Grid size={SMALL_CARD_SIZE}>
        <AutomodsCard />
      </Grid>

      <Grid size={MEDIUM_CARD_SIZE}>
        <ServicesCard />
      </Grid>
      
      <Grid size={SMALL_CARD_SIZE}>
        <MapRotationCard />
      </Grid>

      <Grid size={SMALL_CARD_SIZE}>
        <VIPWatchedCard />
      </Grid>

      <Grid size={SMALL_CARD_SIZE}>
        <FlaggedPlayersCard />
      </Grid>

      <Grid size={SMALL_CARD_SIZE}>
        <ModeratorsCard />
      </Grid>

      <Grid size={LARGE_CARD_SIZE}>
        <LogsCard logs={logs} />
      </Grid>

      <Grid size={MEDIUM_CARD_SIZE}>
        <GamesCard games={games} />
      </Grid>

      <Grid size={MEDIUM_CARD_SIZE}>
        <MapStatsCard games={games} />
      </Grid>
    </Grid>
  );
};

export default Dashboard;
