import { useMemo } from "react";
import { Tabs, Tab, CardContent, Divider } from "@mui/material";
import {
  useLoaderData,
  useSubmit,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  ProfileContainer,
  MainContent,
  SummaryCard,
  DetailCard,
} from "./styled";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import PlayerProfileSummary from "@/components/player/profile/Summary";
import PlayerProfileHeader from "@/components/player/profile/Header";
import { generatePlayerActions } from "@/features/player-action/actions";
import { useActionDialog } from "@/hooks/useActionDialog";
import PlayerProfileStatusTags from "@/components/player/profile/StatusTags";
import ReceivedActions from "./[detail]/received-actions";
import { useGlobalStore } from "@/stores/global-state";

const DETAIL_LINKS = [
  { path: "", label: "Received Actions" },
  { path: "sessions", label: "Sessions" },
  { path: "names", label: "Names" },
  { path: "comments", label: "Comments" },
  { path: "logs", label: "Logs" },
];

export default function PlayerProfilePage() {
  const { profile } = useLoaderData();
  const submit = useSubmit();
  const location = useLocation();
  const navigate = useNavigate();

  const onlinePlayers = useGlobalStore((state) => state.onlinePlayers);
  const server = useGlobalStore((state) => state.serverState);
  const thisOnlinePlayer = useMemo(
    () =>
      onlinePlayers.find((player) => player.player_id === profile.player_id),
    [onlinePlayers, profile.player_id]
  );

  // const playerVip = profile.vips.find(
  //   (vip) => vip.server_number === server?.server_number
  // );
  const isVip = thisOnlinePlayer?.is_vip;
  const isWatched = profile?.watchlist && profile?.watchlist?.is_watched;
  const isBlacklisted = profile?.is_blacklisted;
  const isBanned = profile?.is_banned;
  const actionList = generatePlayerActions({
    multiAction: false,
    onlineAction: !!thisOnlinePlayer,
  });
  const name = profile?.name ?? profile.names[0]?.name ?? "?";
  const avatar = profile?.steaminfo?.profile?.avatar;

  const { openDialog } = useActionDialog();

  const handleActionClick = (recipients) => (action) => {
    openDialog(action, recipients);
  };

  const getActiveTab = () => {
    const path = location.pathname.split("/").pop();
    let activeTab = DETAIL_LINKS.findIndex((link) => link.path === path);
    if (path === profile.player_id) {
      activeTab = 0;
    }
    return activeTab;
  };

  const handleTabChange = (event, newValue) => {
    navigate(DETAIL_LINKS[newValue].path, { replace: true });
  };

  return (
    <ProfileContainer>
      <MainContent>
        <SummaryCard elevation={0} variant="outlined">
          <CardContent>
            <PlayerProfileHeader
              player={profile}
              isOnline={!!thisOnlinePlayer}
              handleActionClick={handleActionClick([
                {
                  player_id: profile.player_id,
                  name,
                },
              ])}
              actionList={actionList}
              avatar={avatar}
              name={name}
            />
            <Divider />
            <PlayerProfileStatusTags
              isVip={isVip}
              isWatched={isWatched}
              isBlacklisted={isBlacklisted}
              isBanned={isBanned}
            />
            <Divider />
            <PlayerProfileSummary
              country={profile.country}
              firstSeen={profile.created}
              lastSeen={profile?.names[0]?.last_seen}
              sessionCount={profile.sessions_count}
              flags={profile.flags}
              totalPlaytime={profile.total_playtime_seconds}
              vip={profile.is_vip}
              otherVips={profile.vip_lists}
              names={profile.names}
              watchlist={profile.watchlist}
            />
          </CardContent>
        </SummaryCard>

        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DetailCard elevation={0} variant="outlined">
            <CardContent>
              <Tabs
                value={getActiveTab()}
                onChange={handleTabChange}
                variant="standard"
                sx={{ mb: 3 }}
              >
                {DETAIL_LINKS.map((link) => (
                  <Tab key={link.path} label={link.label} />
                ))}
              </Tabs>
              {getActiveTab() === 0 && <ReceivedActions />}
              <Outlet context={{ profile, submit }} />
            </CardContent>
          </DetailCard>
        </LocalizationProvider>
      </MainContent>
    </ProfileContainer>
  );
}
