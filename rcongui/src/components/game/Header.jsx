import React from 'react';
import { Board } from './Board';
import Grid from "@mui/material/Grid2"
import { TeamDesktop, TeamMobile } from './Team';
import { styled } from '@mui/styles';
import { Skeleton } from '@mui/material';

const MobileHeaderWrapper = styled(Grid)(({ theme }) => ({
  minHeight: '10rem',
  marginBottom: theme.spacing(1),
  [theme.breakpoints.up('md')]: {
    display: 'none',
  },
}));

const DesktopHeaderWrapper = styled(Grid)(({ theme }) => ({
  minHeight: '10rem',
  marginBottom: theme.spacing(1),
  [theme.breakpoints.down('md')]: {
    display: 'none',
  },
}));

const StyledSkeleton = styled(Skeleton)(() => ({
  minHeight: '10rem',
  margin: '0 1rem',
}));

const DesktopHeader = ({ teamData, boardData }) => {
  return (
    <DesktopHeaderWrapper container component={'header'}>
      <Grid
        xs={4}
        sx={{
          pr: 1,
          borderRight: '1px solid',
          borderRightColor: (theme) => theme.palette.divider,
        }}
      >
        {teamData ? <TeamDesktop data={teamData.allies} /> : <StyledSkeleton />}
      </Grid>
      <Grid xs={4}>
        {boardData ? <Board data={boardData} /> : <StyledSkeleton />}
      </Grid>
      <Grid
        xs={4}
        sx={{
          pl: 1,
          borderLeft: '1px solid',
          borderLeftColor: (theme) => theme.palette.divider,
        }}
      >
        {teamData ? <TeamDesktop data={teamData.axis} /> : <StyledSkeleton />}
      </Grid>
    </DesktopHeaderWrapper>
  );
};

const MobileHeader = ({ teamData, boardData }) => {
  return (
    <MobileHeaderWrapper container component={'header'}>
      <Grid xs={12}>
        {boardData ? <Board data={boardData} /> : <StyledSkeleton />}
      </Grid>
      <Grid xs={6}>
        {teamData ? (
          <TeamMobile data={teamData.allies} align={'start'} />
        ) : (
          <StyledSkeleton />
        )}
      </Grid>
      <Grid xs={6}>
        {teamData ? (
          <TeamMobile data={teamData.axis} align={'end'} />
        ) : (
          <StyledSkeleton />
        )}
      </Grid>
    </MobileHeaderWrapper>
  );
};

export const Header = ({ teamData, gameState }) => {
  return (
    <React.Fragment>
      <MobileHeader teamData={teamData} boardData={gameState} />
      <DesktopHeader teamData={teamData} boardData={gameState} />
    </React.Fragment>
  );
};
