import { Avatar, Badge, Box, Stack, Tooltip, Typography } from '@mui/material';
import { styled } from '@mui/styles';
import { CountryFlag } from '../../../../components/CountryFlag';

// TODO
// What is the type prop for?
const RoleAvatar = styled(Avatar, {
  shouldForwardProp: (prop) => prop !== 'type',
})(({ theme, type }) => ({
  width: 22,
  height: 22,
  marginLeft: '6px',
  border: `2px solid ${theme.palette.background.paper}`,
  background: theme.palette.info.dark,
}));

export const columns = [
  // {
  //   field: 'team',
  //   headerName: 'Team',
  //   width: 50,
  //   renderCell: (params) => {
  //     const [allies, axis] = ['1001546200681566330', '1001525586839208006'];
  //     const src = (team) =>
  //       `https://cdn.discordapp.com/emojis/${team === 'axis' ? axis : allies}.webp?size=128&quality=lossless`;

  //     return (
  //       <Box
  //         sx={{
  //           display: 'flex',
  //           alignItems: 'center',
  //           justifyContent: 'center',
  //           height: '100%',
  //           width: '100%',
  //         }}
  //       >
  //         <img
  //           src={src(params.value)}
  //           alt={params.value}
  //           width={20}
  //           height={'auto'}
  //         />
  //       </Box>
  //     );
  //   },
  // },
  {
    field: 'assignment',
    headerName: 'Assignment',
    width: 75,
    valueGetter: (value, row) => {
      return `${row.team}-${row.unit_name}-${row.role}`;
    },
    renderCell: (params) => {
      let src = `/icons/roles/${params.row.role}.png`;
      return (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            width: '100%',
          }}
        >
          <Badge
            overlap="circular"
            title={`${params.row.team}-${params.row.unit_name}-${params.row.role}`.toUpperCase()}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            badgeContent={
              <RoleAvatar
                variant="circular"
                alt={'Role' + params.value}
                type={params.value}
                src={src}
                slotProps={{
                  img: {
                    sx: {
                      width: '80%',
                      height: '80%',
                    }
                  }
                }}
              >
                ?
              </RoleAvatar>
            }
          >
            <Avatar
              sx={{
                width: 28,
                height: 28,
                fontWeight: '600',
                fontSize: '23px',
                paddingRight: '4px',
                background: (theme) =>
                  params.row.team === 'axis'
                    ? theme.palette.secondary.main
                    : theme.palette.primary.main,
                color: (theme) =>
                  params.row.team === 'axis'
                    ? theme.palette.secondary.contrastText
                    : theme.palette.primary.contrastText,
              }}
              variant="square"
            >
              {params.row?.unit_name?.[0].toUpperCase() ?? '?'}
            </Avatar>
          </Badge>
        </Box>
      );
    },
  },
  {
    field: 'level',
    headerName: 'Level',
    width: 50,
  },
  {
    field: 'name',
    headerName: 'Name',
    width: 250,
  },
  {
    field: 'country',
    headerName: 'Country',
    width: 50,
    renderCell: (params) => {
      if (!params.value || params.value === 'private') return null;

      return (
        <CountryFlag country={params.value.toLowerCase()} />
      );
    },
  },
  {
    field: 'player_id',
    headerName: 'ID',
  },
  {
    field: 'is_vip',
    headerName: 'VIP',
    type: 'boolean',
    width: 50,
  },
  {
    field: 'flags',
    headerName: 'Flags',
    width: 75,
    renderCell: (params) => {
      const flags = params.value;
      if (!flags || flags.length === 0) return null;
      const flagsCount = 2;
      return (
        <Stack spacing={0.25} direction={'row'} alignItems={'center'}>
          {flags.slice(0, flagsCount).map(({ flag, comment: note, modified }) => (
            <Tooltip title={note} key={modified}>
              <Box>{flag}</Box>
            </Tooltip>
          ))}
          {flags.length - flagsCount > 0 ? <Typography>{`+${flags.length - flagsCount}`}</Typography> : null}
        </Stack>
      )
    },
  },
  {
    field: 'current_playtime_seconds',
    headerName: 'Playtime',
    type: 'number',
    valueGetter: (value) => Math.floor(value / 60),
    width: 75,
  },
  {
    field: 'sessions_count',
    headerName: '# Visits',
    type: 'number',
    width: 75,
  },
  // {
  //   field: 'punish_times',
  //   headerName: '# Punish',
  //   type: 'number',
  //   width: 50,
  //   valueFormatter: (value) => (value === 0 ? '' : value),
  // },
  // {
  //   field: 'kicked_times',
  //   headerName: '# Kick',
  //   type: 'number',
  //   width: 50,
  //   valueFormatter: (value) => (value === 0 ? '' : value),
  // },
  // {
  //   field: 'tempban_times',
  //   headerName: '# TempBan',
  //   type: 'number',
  //   width: 50,
  //   valueFormatter: (value) => (value === 0 ? '' : value),
  // },
  // {
  //   field: 'permaban_times',
  //   headerName: '# PermaBan',
  //   type: 'number',
  //   width: 50,
  //   valueFormatter: (value) => (value === 0 ? '' : value),
  // },
];