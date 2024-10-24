import {
  Typography,
  Divider,
  Stack,
  Box,
} from '@mui/material';
import { styled } from '@mui/material';
import Grid from "@mui/material/Grid2"

const StyledStack = styled(Stack)(({ theme }) => ({
  padding: 0,
  [theme.breakpoints.up('md')]: {
    paddingRight: theme.spacing(1),
    paddingLeft: theme.spacing(1),
  },
}));

export const Board = ({ data, ...props }) => {
  return (
    <StyledStack>
      <Typography textAlign={'center'} variant="h6" component={'span'}>
        {data.raw_time_remaining}
      </Typography>
      <Divider variant="middle" />
      <Grid
        container
        columnSpacing={1}
        justifyContent={'center'}
        sx={{ py: 0.5 }}
        alignContent={'center'}
      >
        <Grid
          size={4}
          sx={{
            display: 'flex',
            justifyContent: 'start',
            alignItems: 'center',
          }}
        >
          <Box width={50} height={50} component={"img"} alt="Allies" src={`/icons/teams/${data.current_map.map.allies.name}.webp`} />
        </Grid>
        <Grid container sx={{ textAlign: 'center' }} size={4}>
          <Grid size={5}>
            <Typography variant={'h2'} component={'span'}>
              {data.allied_score}
            </Typography>
          </Grid>
          <Grid size={2}>
            <Typography variant={'h2'} component={'span'}>
              :
            </Typography>
          </Grid>
          <Grid size={5}>
            <Typography variant={'h2'} component={'span'}>
              {data.axis_score}
            </Typography>
          </Grid>
          <Grid size={12}>
            <Typography variant="subtitle2">{`[ ${data.num_allied_players} vs ${data.num_axis_players} ]`}</Typography>
          </Grid>
        </Grid>
        <Grid
          size={4}
          sx={{
            display: 'flex',
            justifyContent: 'end',
            alignItems: 'center',
          }}
        >
          <Box width={50} height={50} component={"img"} alt="Axis" src={`/icons/teams/${data.current_map.map.axis.name}.webp`} />
        </Grid>
      </Grid>
      <Divider variant="middle" />
      <Grid container>
        <Grid size={3}>
          <Typography textAlign={'left'} variant="subtitle2">
            {`AVG. ${data.allies.avg_level}`}
          </Typography>
        </Grid>
        <Grid size={6}>
          <Typography textAlign={'center'} variant="subtitle2">
            {data.current_map.map.pretty_name}
          </Typography>
        </Grid>
        <Grid size={3}>
          <Typography textAlign={'right'} variant="subtitle2">
            {`AVG. ${data.axis.avg_level}`}
          </Typography>
        </Grid>
      </Grid>
      <Grid container>
        <Grid size={3}>
          <Typography textAlign={'left'} variant="subtitle2">
            {`MED. ${data.allies.med_level}`}
          </Typography>
        </Grid>
        <Grid size={6}>
          <Typography textAlign={'center'} variant="subtitle2">
            {data.current_map.game_mode.toUpperCase()}
          </Typography>
        </Grid>
        <Grid size={3}>
          <Typography textAlign={'right'} variant="subtitle2">
            {`MED. ${data.axis.med_level}`}
          </Typography>
        </Grid>
      </Grid>
    </StyledStack>
  );
};
