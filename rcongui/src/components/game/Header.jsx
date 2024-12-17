import React from 'react';
import { Board } from './Board';
import Grid from "@mui/material/Grid2"
import { TeamDesktop, TeamMobile } from './Team';
import { styled } from '@mui/material';
import { Skeleton } from '@mui/material';

const MobileHeaderWrapper = styled(Grid)(({ theme }) => ({
  minHeight: '4rem',
  marginBottom: theme.spacing(1),
  [theme.breakpoints.up('md')]: {
    display: 'none',
  },
}));

const DesktopHeaderWrapper = styled(Grid)(({ theme }) => ({
  minHeight: '4rem',
  marginBottom: theme.spacing(1),
  [theme.breakpoints.down("md")]: {
    display: 'none',
  },
}));

const StyledSkeleton = styled(Skeleton)(() => ({
  minHeight: '4',
  margin: '0 1rem',
}));
  
const DesktopHeader = ({ data }) => {
  return (
    <DesktopHeaderWrapper container component={'header'}>
      <Grid
        size={4}
        sx={{
          pr: 1,
          borderRight: '1px solid',
          borderRightColor: (theme) => theme.palette.divider,
        }}
      >
        {data ? <TeamDesktop data={data.allies} /> : <StyledSkeleton />}
      </Grid>
      <Grid size={4}>
        {data ? <Board data={data} /> : <StyledSkeleton />}
      </Grid>
      <Grid
        size={4}
        sx={{
          pl: 1,
          borderLeft: '1px solid',
          borderLeftColor: (theme) => theme.palette.divider,
        }}
      >
        {data ? <TeamDesktop data={data.axis} /> : <StyledSkeleton />}
      </Grid>
    </DesktopHeaderWrapper>
  );
};

const MobileHeader = ({ data }) => {
  return (
    <MobileHeaderWrapper container component={'header'}>
      <Grid size={12}>
        {data ? <Board data={data} /> : <StyledSkeleton />}
      </Grid>
      <Grid size={6} sx={{ borderRight: '1px solid', borderRightColor: (theme) => theme.palette.divider }}>
        {data ? (
          <TeamMobile data={data.allies} align={'start'} />
        ) : (
          <StyledSkeleton />
        )}
      </Grid>
      <Grid size={6}>
        {data ? (
          <TeamMobile data={data.axis} align={'end'} />
        ) : (
          <StyledSkeleton />
        )}
      </Grid>
    </MobileHeaderWrapper>
  );
};

export const Header = ({ data }) => {
  return (
    <React.Fragment>
      <MobileHeader data={data} />
      <DesktopHeader data={data} />
    </React.Fragment>
  );
};
