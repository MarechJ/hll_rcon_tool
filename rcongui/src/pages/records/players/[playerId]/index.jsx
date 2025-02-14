import { useState } from 'react';
import {
  Typography,
  Tabs,
  Tab,
  TextField,
  MenuItem,
  CardContent,
  CardHeader,
  Alert,
  AlertTitle,
  Button,
  Box,
  Stack,
  Divider,
  Tooltip,
} from '@mui/material';
import { Warning as WarningIcon, Star as StarIcon } from '@mui/icons-material';
import { useLoaderData, useSubmit, Outlet, Await, Link, useLocation, useNavigate } from 'react-router-dom';
import { Suspense } from 'react';
import {
  ProfileContainer,
  TopSection,
  PlayerInfo,
  PlayerAvatar,
  PlayerNameSection,
  BadgesContainer,
  StyledChip,
  ActiveBanAlert,
  MainContent,
  SummaryCard,
  DetailCard,
  ScrollableContent,
  ListItem,
  FilterSection,
  StatItem,
  PenaltiesGrid,
  StatusChip,
  StatusAlert,
  VipStatusSection,
  VipChip,
} from './styled';

// Loading placeholder component
const LoadingPlaceholder = () => (
  <Box sx={{ p: 4, textAlign: 'center' }}>
    <Typography>Loading...</Typography>
  </Box>
);

const DETAIL_LINKS = [
  { path: 'sessions', label: 'Sessions' },
  { path: 'activities', label: 'Activities' },
  { path: 'names', label: 'Names' },
  { path: 'comments', label: 'Comments' },
  { path: 'logs', label: 'Logs' },
];

export default function PlayerProfilePage() {
  const { profile, messages, connectionInfo } = useLoaderData();
  const submit = useSubmit();
  const location = useLocation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [newComment, setNewComment] = useState('');
  const [filters, setFilters] = useState({
    sessions: { search: '', startDate: '', endDate: '' },
    actions: { search: '', type: '' },
    names: { search: '' },
    comments: { search: '', author: '', startDate: '', endDate: '' },
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatPlaytime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const formatVipExpiration = (date) => {
    const expirationDate = new Date(date);
    const now = new Date();
    const diffTime = Math.abs(expirationDate - now);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (expirationDate.getFullYear() >= 3000) {
      return 'Never';
    }
    
    return `${diffDays} days`;
  };

  const handleFilterChange = (tab, key, value) => {
    setFilters((prev) => ({ ...prev, [tab]: { ...prev[tab], [key]: value } }));
  };

  const handleCommentSubmit = (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('player_id', profile.player_id);
    formData.append('comment', newComment);
    submit(formData, { method: 'post' });
    setNewComment('');
  };

  const filterData = (data, tab) => {
    return data.filter((item) => {
      const searchLower = filters[tab].search.toLowerCase();
      switch (tab) {
        case 'sessions':
          return (
            (item.start.includes(filters.sessions.startDate) || !filters.sessions.startDate) &&
            (item.end?.includes(filters.sessions.endDate) || !filters.sessions.endDate) &&
            (item.start.toLowerCase().includes(searchLower) || item.end?.toLowerCase().includes(searchLower))
          );
        case 'actions':
          return (
            item.action_type.includes(filters.actions.type) &&
            (item.reason.toLowerCase().includes(searchLower) || item.by.toLowerCase().includes(searchLower))
          );
        case 'names':
          return item.name.toLowerCase().includes(searchLower);
        case 'comments':
          return (
            item.content.toLowerCase().includes(searchLower) &&
            item.by.includes(filters.comments.author) &&
            (item.creation_time.includes(filters.comments.startDate) || !filters.comments.startDate) &&
            (item.creation_time.includes(filters.comments.endDate) || !filters.comments.endDate)
          );
        default:
          return true;
      }
    });
  };

  const getActiveTab = () => {
    const path = location.pathname.split('/').pop();
    return DETAIL_LINKS.findIndex(link => link.path === path);
  };

  const handleTabChange = (event, newValue) => {
    navigate(DETAIL_LINKS[newValue].path);
  };

  return (
    <Suspense fallback={<LoadingPlaceholder />}>
      <Await resolve={profile}>
        {(resolvedProfile) => (
          <ProfileContainer>
            <TopSection>
              <PlayerInfo>
                <PlayerAvatar>VL</PlayerAvatar>
                <PlayerNameSection>
                  <Typography variant="h6" component="h1">
                    {resolvedProfile.names[0].name}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Player ID: {resolvedProfile.player_id}
                  </Typography>
                </PlayerNameSection>
              </PlayerInfo>
              <BadgesContainer>
                {resolvedProfile.vips.map((vip, index) => (
                  <StyledChip
                    key={index}
                    icon={<StarIcon />}
                    label={`VIP ${vip.server_number} (${formatVipExpiration(vip.expiration)})`}
                    className="vip"
                    size="small"
                  />
                ))}
                {resolvedProfile.flags.map((flag, index) => (
                  <StyledChip
                    key={index}
                    label={`${flag.flag} ${flag.comment}`}
                    className="trusted"
                    size="small"
                  />
                ))}
              </BadgesContainer>
            </TopSection>

            <MainContent>
              <SummaryCard elevation={0} variant="outlined">
                <CardHeader title="Player Summary" />
                <CardContent>
                  <StatItem>
                    <Typography variant="body2">Total Playtime:</Typography>
                    <Typography variant="body2">{formatPlaytime(resolvedProfile.total_playtime_seconds)}</Typography>
                  </StatItem>
                  <StatItem>
                    <Typography variant="body2">Sessions:</Typography>
                    <Typography variant="body2">{resolvedProfile.sessions_count}</Typography>
                  </StatItem>
                  <StatItem>
                    <Typography variant="body2">Account Created:</Typography>
                    <Typography variant="body2">{formatDate(resolvedProfile.created)}</Typography>
                  </StatItem>

                  {resolvedProfile.vips?.length > 0 && (
                    <VipStatusSection>
                      <Typography variant="subtitle2">VIP Status</Typography>
                      {resolvedProfile.vips.map((vip, index) => (
                        <VipChip
                          key={index}
                          icon={<StarIcon />}
                          label={`Server #${vip.server_number}`}
                          size="small"
                        />
                      ))}
                      <Typography variant="caption" color="text.secondary">
                        Expires: {formatVipExpiration(resolvedProfile.vips[0].expiration)}
                      </Typography>
                    </VipStatusSection>
                  )}

                  <Typography variant="subtitle2" sx={{ mt: 3, mb: 2 }}>
                    Status
                  </Typography>
                  
                  {resolvedProfile.active_ban && (
                    <StatusAlert severity="error" variant="outlined">
                      <AlertTitle>Active Ban</AlertTitle>
                      <Typography variant="body2">
                        Type: {resolvedProfile.active_ban.type}
                      </Typography>
                      <Typography variant="body2">
                        Reason: {resolvedProfile.active_ban.reason}
                      </Typography>
                      <Typography variant="body2">
                        By: {resolvedProfile.active_ban.by}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Until: {formatDate(resolvedProfile.active_ban.end_time)}
                      </Typography>
                    </StatusAlert>
                  )}

                  {resolvedProfile.watchlist && resolvedProfile.watchlist.is_watched && (
                    <StatusAlert severity="warning" variant="outlined">
                      <AlertTitle>Being Watched</AlertTitle>
                      <Typography variant="body2">
                        Reason: {resolvedProfile.watchlist.reason}
                      </Typography>
                      <Typography variant="body2">
                        By: {resolvedProfile.watchlist.by}
                      </Typography>
                    </StatusAlert>
                  )}

                  {resolvedProfile.is_blacklisted && (
                    <StatusAlert severity="error" variant="outlined">
                      <AlertTitle>Blacklisted</AlertTitle>
                      {resolvedProfile.blacklists.length > 0 && (
                        <>
                          <Typography variant="body2">
                            Reason: {resolvedProfile.blacklists[0].reason}
                          </Typography>
                          <Typography variant="body2">
                            By: {resolvedProfile.blacklists[0].by}
                          </Typography>
                        </>
                      )}
                    </StatusAlert>
                  )}

                  <Typography variant="subtitle2" sx={{ mt: 3, mb: 2 }}>
                    Flags
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                    {resolvedProfile.flags.map((flag, index) => (
                      <Tooltip key={index} title={flag.comment} arrow placement="top">
                        <StyledChip
                          label="Trusted"
                          className="trusted"
                        />
                      </Tooltip>
                    ))}
                  </Box>

                  <Typography variant="subtitle2" sx={{ mt: 3, mb: 2 }}>
                    Penalties
                  </Typography>
                  <PenaltiesGrid>
                    <Typography>Kicks: {resolvedProfile.penalty_count.KICK}</Typography>
                    <Typography>Punishes: {resolvedProfile.penalty_count.PUNISH}</Typography>
                    <Typography>Temp Bans: {resolvedProfile.penalty_count.TEMPBAN}</Typography>
                    <Typography>Perma Bans: {resolvedProfile.penalty_count.PERMABAN}</Typography>
                  </PenaltiesGrid>
                </CardContent>
              </SummaryCard>

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

                  <Outlet context={{ profile: resolvedProfile, submit }} />
                </CardContent>
              </DetailCard>

            </MainContent>
          </ProfileContainer>
        )}
      </Await>
    </Suspense>
  );
}
