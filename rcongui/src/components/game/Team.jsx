import Grid from "@mui/material/Grid2"
import Man4Icon from '@mui/icons-material/Man4';
import Points, { NumberText } from './Points';
import { Avatar, Divider } from '@mui/material';
import { extractTeamState } from '@/utils/extractPlayers';

const teamMetrics = ['combat', 'offense', 'defense', 'support'];

const teamStats = ['kills', 'deaths'];

const teamRoles = ['armycommander', 'armor', 'infantry', 'recon'];

const makeTeam = (n) =>
  Array.from({ length: n })
    .fill(null)
    .map(() => (
      <Man4Icon
        sx={{
          margin: '0 -0.45rem',
          fontSize: '1.25rem',
          color: (theme) => theme.palette.primary.main,
        }}
      />
    ));

const roleSrc = (role) => `/icons/roles/${role}.png`;

export const TeamMobile = ({ data, align }) => {
  const team = data ?? {};
  return (
    <>
      <Grid container xs={12} sx={{ textAlign: 'center' }}>
        {teamMetrics.map((metric) => (
          <Grid
            key={metric}
            xs={12}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: align,
              gap: 1,
            }}
          >
            <Points value={team[metric]} type={metric} direction={align === 'start' ? 'left' : 'right'} />
          </Grid>
        ))}
      </Grid>
      <Grid container xs={12} sx={{ textAlign: 'center' }}>
        {teamStats.map((stat) => (
          <Grid
            key={stat}
            xs={12}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: align,
              gap: 1,
            }}
          >
            <Points value={team[stat]} type={stat} direction={align === 'start' ? 'left' : 'right'}  />
          </Grid>
        ))}
      </Grid>
    </>
  );
};

export const TeamDesktop = ({ data }) => {
  const team = data ?? {};

  const roleCounts = extractTeamState(team);

  const counts = teamRoles.map((role) => ({
    role,
    count: roleCounts[role],
  }));

  return (
    <>
      <Grid container xs={12} sx={{ height: '1.5rem', textAlign: 'center' }}>
        {teamMetrics.map((metric) => (
          <Grid
            key={metric}
            xs={3}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'start',
              gap: 1,
            }}
          >
            <Points value={team[metric]} type={metric} />
          </Grid>
        ))}
      </Grid>
      <Grid container xs={12} sx={{ height: '1.5rem', textAlign: 'center' }}>
        {teamStats.map((stat) => (
          <Grid
            key={stat}
            xs={6}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'start',
              gap: 1,
            }}
          >
            <Points value={team[stat]} type={stat} />
          </Grid>
        ))}
      </Grid>
      <Divider sx={{ my: 0.5 }} />
      <Grid container xs={12}>
        {counts.map(({ role, count }) => (
          <Grid key={role} container xs={12}>
            <Grid xs={1}>
              <Avatar
                src={roleSrc(role)}
                alt={role}
                sx={{ width: '1rem', height: '1rem' }}
              />
            </Grid>
            <Grid xs={10}>{makeTeam(count)}</Grid>
            <Grid xs={1}>
              <NumberText>{count}</NumberText>
            </Grid>
          </Grid>
        ))}
      </Grid>
    </>
  );
};
