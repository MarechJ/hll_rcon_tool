import { useState } from 'react';
import {
  Typography,
  TextField,
  MenuItem,
  CardContent,
  Button,
  Box,
  InputAdornment,
  Divider,
  Stack,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { useParams, useOutletContext, Form, useSearchParams, useSubmit, useRevalidator } from 'react-router-dom';
import {
  DetailCard,
  ScrollableContent,
  ListItem,
  FilterSection,
} from '../styled';
import dayjs from 'dayjs';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import PlayerLogs from './logs';

export default function PlayerDetailView() {
  const { detail } = useParams();
  const { profile, submit } = useOutletContext();
  const [searchParams, setSearchParams] = useSearchParams();
  const revalidator = useRevalidator();
  const [newComment, setNewComment] = useState('');
  const [filters, setFilters] = useState({
    sessions: { 
      search: '', 
      startDate: null, 
      endDate: null 
    },
    actions: { search: '', type: '' },
    names: { search: '' },
    comments: { 
      search: '', 
      author: '', 
      startDate: null, 
      endDate: null 
    },
  });

  const formatDate = (dateString) => {
    return dayjs(dateString).format('lll');
  };

  const handleFilterChange = (tab, key, value) => {
    setFilters((prev) => ({ ...prev, [tab]: { ...prev[tab], [key]: value } }));
  };

  const handleSessionCountChange = (event) => {
    const value = event.target.value;
    if (value && value > 0) {
      setSearchParams(prev => {
        prev.set('num_sessions', value);
        return prev;
      });
    }
  };

  const handleCommentSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('player_id', profile.player_id);
    formData.append('comment', newComment);
    
    const result = await submit(formData, { 
      method: 'post',
      replace: true,
    });

    if (result?.ok) {
      setNewComment('');
      revalidator.revalidate();
    }
  };

  const filterData = (data, tab) => {
    return data.filter((item) => {
      const searchLower = filters[tab].search.toLowerCase();
      switch (tab) {
        case 'sessions':
          const startDate = filters.sessions.startDate ? dayjs(filters.sessions.startDate) : null;
          const endDate = filters.sessions.endDate ? dayjs(filters.sessions.endDate) : null;
          const sessionStart = dayjs(item.start);
          const sessionEnd = item.end ? dayjs(item.end) : null;

          return (
            (!startDate || sessionStart.isAfter(startDate)) &&
            (!endDate || (sessionEnd && sessionEnd.isBefore(endDate))) &&
            (sessionStart.format('lll').toLowerCase().includes(searchLower) || 
             (sessionEnd && sessionEnd.format('lll').toLowerCase().includes(searchLower)))
          );
        case 'actions':
          return (
            item.action_type.includes(filters.actions.type) &&
            (item.reason.toLowerCase().includes(searchLower) || item.by.toLowerCase().includes(searchLower))
          );
        case 'names':
          return item.name.toLowerCase().includes(searchLower);
        case 'comments':
          const commentStartDate = filters.comments.startDate ? dayjs(filters.comments.startDate) : null;
          const commentEndDate = filters.comments.endDate ? dayjs(filters.comments.endDate) : null;
          const commentDate = dayjs(item.creation_time);

          return (
            item.content.toLowerCase().includes(searchLower) &&
            item.by.includes(filters.comments.author) &&
            (!commentStartDate || commentDate.isAfter(commentStartDate)) &&
            (!commentEndDate || commentDate.isBefore(commentEndDate))
          );
        default:
          return true;
      }
    });
  };

  const renderContent = () => {
    switch (detail) {
      case 'sessions':
        return (
          <div>
            <FilterSection>
              <TextField
                sx={{ maxWidth: '200px' }}
                label="Number of sessions"
                type="number"
                value={searchParams.get('num_sessions') || '10'}
                onChange={handleSessionCountChange}
                size="small"
                InputProps={{
                  endAdornment: <InputAdornment position="end">sessions</InputAdornment>,
                }}
                inputProps={{
                  min: 1,
                  max: 1000,
                }}
              />
              <Box className="date-inputs">
                <LocalizationProvider dateAdapter={AdapterDayjs}>
                  <DateTimePicker
                    label="Start Date"
                    value={filters.sessions.startDate}
                    format='lll'
                    onChange={(newValue) => handleFilterChange('sessions', 'startDate', newValue)}
                    slotProps={{ textField: { size: 'small' } }}
                  />
                </LocalizationProvider>
                <LocalizationProvider dateAdapter={AdapterDayjs}>
                  <DateTimePicker
                    label="End Date"
                  value={filters.sessions.endDate}
                  format='lll'
                  onChange={(newValue) => handleFilterChange('sessions', 'endDate', newValue)}
                    slotProps={{ textField: { size: 'small' } }}
                  />
                </LocalizationProvider>
              </Box>
            </FilterSection>
            <Stack direction="row" justifyContent="space-between" sx={{ p: 2 }}>
              <Typography variant="body2">Total sessions: {filterData(profile.sessions, 'sessions').length}</Typography>
              <Typography variant="body2">
                Total playtime: {filterData(profile.sessions, 'sessions').reduce((acc, session) => 
                  acc + (session.end === null ? 0 : dayjs(session.end).diff(dayjs(session.start), 'minutes')), 0)
                } minutes
              </Typography>
            </Stack>
            <Divider />
            <ScrollableContent>
              {filterData(profile.sessions, 'sessions').map((session, index) => (
                <ListItem sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', justifyContent: 'space-between' }} key={index}>
                  <Typography variant="body2">Start: {formatDate(session.start)}</Typography>
                  <Typography variant="body2">
                    Duration: {session.end === null ? 'Unknown' : dayjs(session.end).diff(dayjs(session.start), 'minutes') + ' minutes'}
                  </Typography>
                  <Typography variant="body2">End: {session.end === null ? 'Unknown' : formatDate(session.end)}</Typography>
                </ListItem>
              ))}
            </ScrollableContent>
          </div>
        );

      case 'activities':
        return (
          <div>
            <FilterSection>
              <TextField
                label="Search actions"
                value={filters.actions.search}
                onChange={(e) => handleFilterChange('actions', 'search', e.target.value)}
                size="small"
              />
              <TextField
                select
                label="Action Type"
                value={filters.actions.type}
                onChange={(e) => handleFilterChange('actions', 'type', e.target.value)}
                size="small"
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="TEMPBAN">TEMPBAN</MenuItem>
                <MenuItem value="PUNISH">PUNISH</MenuItem>
                <MenuItem value="KICK">KICK</MenuItem>
                <MenuItem value="MESSAGE">MESSAGE</MenuItem>
              </TextField>
            </FilterSection>
            <ScrollableContent>
              {filterData(profile.received_actions, 'actions').map((action, index) => (
                <ListItem key={index}>
                  <Typography variant="subtitle1">{action.action_type}</Typography>
                  <Typography>Reason: {action.reason}</Typography>
                  <Typography>By: {action.by}</Typography>
                  <Typography>Time: {formatDate(action.time)}</Typography>
                </ListItem>
              ))}
            </ScrollableContent>
          </div>
        );

      case 'names':
        return (
          <div>
            <FilterSection>
              <TextField
                label="Search names"
                value={filters.names.search}
                onChange={(e) => handleFilterChange('names', 'search', e.target.value)}
                size="small"
                fullWidth
              />
            </FilterSection>
            <ScrollableContent>
              {filterData(profile.names, 'names').map((name, index) => (
                <ListItem key={index}>
                  <Typography variant="subtitle1">{name.name}</Typography>
                  <Typography>Last seen: {formatDate(name.last_seen)}</Typography>
                </ListItem>
              ))}
            </ScrollableContent>
          </div>
        );

      case 'comments':
        return (
          <div>
            <Form onSubmit={handleCommentSubmit}>
              <FilterSection>
                <TextField
                  label="New Comment"
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  size="small"
                  fullWidth
                  multiline
                  rows={2}
                />
                <Button type="submit" variant="contained" disabled={!newComment.trim()}>
                  Add Comment
                </Button>
              </FilterSection>
            </Form>
            <FilterSection>
              <TextField
                label="Search comments"
                value={filters.comments.search}
                onChange={(e) => handleFilterChange('comments', 'search', e.target.value)}
                size="small"
              />
              <TextField
                label="Author"
                value={filters.comments.author}
                onChange={(e) => handleFilterChange('comments', 'author', e.target.value)}
                size="small"
              />
              <Box className="date-inputs">
                <DateTimePicker
                  label="Start Date"
                  value={filters.comments.startDate}
                  onChange={(newValue) => handleFilterChange('comments', 'startDate', newValue)}
                  slotProps={{ textField: { size: 'small' } }}
                />
                <DateTimePicker
                  label="End Date"
                  value={filters.comments.endDate}
                  onChange={(newValue) => handleFilterChange('comments', 'endDate', newValue)}
                  slotProps={{ textField: { size: 'small' } }}
                />
              </Box>
            </FilterSection>
            <ScrollableContent>
              {filterData(profile.comments, 'comments').map((comment, index) => (
                <ListItem key={index}>
                  <Typography>{comment.content}</Typography>
                  <Typography>By: {comment.by}</Typography>
                  <Typography>Time: {formatDate(comment.creation_time)}</Typography>
                </ListItem>
              ))}
            </ScrollableContent>
          </div>
        );

      case 'logs':
        return <PlayerLogs />;

      default:
        return null;
    }
  };

  return (
    <DetailCard elevation={0} variant="outlined">
      <CardContent>
        {renderContent()}
      </CardContent>
    </DetailCard>
  );
} 