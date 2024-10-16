import { Suspense } from 'react';
import MuiAvatar from '@mui/material/Avatar';
import MuiListItemAvatar from '@mui/material/ListItemAvatar';
import MenuItem from '@mui/material/MenuItem';
import ListItemText from '@mui/material/ListItemText';
import ListSubheader from '@mui/material/ListSubheader';
import Select, { selectClasses } from '@mui/material/Select';
import { styled } from '@mui/material/styles';
import DevicesRoundedIcon from '@mui/icons-material/DevicesRounded';
import { Await, useLoaderData } from 'react-router-dom';
import { Box, Skeleton } from '@mui/material';
import { ErrorSection } from '../shared/ErrorSection';

const Avatar = styled(MuiAvatar)(({ theme }) => ({
  width: 28,
  height: 28,
  backgroundColor: theme.palette.background.paper,
  color: theme.palette.text.secondary,
  border: `1px solid ${theme.palette.divider}`,
}));

const ListItemAvatar = styled(MuiListItemAvatar)({
  minWidth: 0,
  marginRight: 12,
});

const SelectSkeleton = styled(Skeleton)(({ theme }) => ({
  height: 56,
  width: 215,
}))

export default function SelectContent() {
  const data = useLoaderData();

  const handleChange = (servers) => (event) => {
    const serverNumber = Number(event.target.value)
    const selectedServer = servers.find(server => server.server_number === serverNumber)
    if (!selectedServer) {
      return
    }
    let link = "";
    if (selectedServer.link) {
      link = new URL(`${selectedServer.link}${window.location.hash}`);
    } else {
      const regex = /:(\d+)/gm;
      link = new URL(
        window.location.href.replace(regex, `:${selectedServer.port}`)
      );
    }
    window.location.replace(link)
  };

  return (
    <Suspense fallback={<Box sx={{ width: 215, height: 56, p: "8px" }}>"Loading..."</Box>}>
      <Await errorElement={<ErrorSection />} resolve={Promise.all([data.thisServer, data.otherServers])}>
        {([thisServer, otherServers]) => {
          const servers = [thisServer, ...otherServers];
          return (
            <Select
              labelId="server-select"
              id="server-simple-select"
              defaultValue={thisServer.server_number}
              onChange={handleChange(servers)}
              displayEmpty
              inputProps={{ 'aria-label': 'Select server' }}
              fullWidth
              MenuProps={{
                PaperProps: {
                  sx: {
                    '& .MuiMenuItem-root:not(:last-child)': {
                      mb: 1,
                    },
                  },
                },
              }}
              sx={{
                maxHeight: 56,
                width: 215,
                '&.MuiList-root': {
                  p: '8px',
                },
                [`& .${selectClasses.select}`]: {
                  display: 'flex',
                  alignItems: 'center',
                  gap: '2px',
                  pl: 1,
                },
              }}
            >
              <ListSubheader sx={{ pt: 0 }}>Servers</ListSubheader>
              {servers?.map((server) => (
                <MenuItem key={server.server_number} value={server.server_number}>
                  <ListItemAvatar>
                    <Avatar alt={server.name ?? "<server_name>"}>
                      <DevicesRoundedIcon sx={{ fontSize: '1rem' }} />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }} primary={server.name ?? "<server_name>"} secondary={`Server - ${server.server_number}` ?? "<server_number>"} />
                </MenuItem>
              ))}
            </Select>
          )
        }}
      </Await>
    </Suspense>
  );
}
