import React from 'react';
import Grid from '@mui/material/Grid2';
import LogsLiveList from '@/components/LogsLiveList';
import PlayersTable from '@/components/PlayersTable';
import { get } from '@/utils/fetchUtils';
import { useInterval } from '@/hooks/useInterval';
import { Box } from '@mui/material';
import { extractPlayers, extractTeamState } from '@/utils/extractPlayers';
import { columns, playerToRow } from '@/pages/views/live/columns';
import { styled } from '@mui/styles';
import { Header } from '@/components/game/Header';

const ViewWrapper = styled(Box)(({ theme }) => ({}));

const interval = 30;

let getTeamView = () => get('get_team_view');
let getGameState = () => get('get_gamestate');

if (import.meta.env.DEV) {
  getTeamView = () =>
    new Promise((res) =>
      setTimeout(() => res(new Response(JSON.stringify(teamViewResult))), 1000)
    );

  getGameState = () =>
    new Promise((res) =>
      setTimeout(() => res(new Response(JSON.stringify(gameStateResult))), 1000)
    );
}

const LiveView = () => {
  const { data: teamData } = useInterval(getTeamView, interval * 1000);
  const { data: gameState } = useInterval(getGameState, interval * 1000);

  const gameStateProp = React.useMemo(() => {
    if (gameState && teamData) {
      return {
        ...gameState.result,
        allies: extractTeamState(teamData?.result?.allies ?? {}),
        axis: extractTeamState(teamData?.result?.axis ?? {}),
      };
    }

    return null;
  }, [gameState, teamData]);

  const rows = React.useMemo(() => {
    if (!teamData) return [];
    const players = extractPlayers(teamData.result);
    return players.map(playerToRow)
  }, [teamData]);

  return (
    <ViewWrapper>
      <Header teamData={teamData?.result} gameState={gameStateProp} />
      <Grid container spacing={1}>
        <Grid xs={12} md={6} xl={'auto'}>
          <PlayersTable data={teamData ?? {}} rows={rows} columns={columns}/>
        </Grid>
        <Grid xs={12} md={6} xl>
          <LogsLiveList />
        </Grid>
      </Grid>
    </ViewWrapper>
  );
};

export default LiveView;