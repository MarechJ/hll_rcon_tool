import {
  Avatar,
  Box,
  Button,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { FormCard, Wrapper } from './cards';
import { Form } from 'react-router-dom';
import { getMapImageUrl, getMapName } from '../Scoreboard/utils';

const simplifyStatusResult = (status) => {
  if (!status.selection.length) return;

  let selection = new Map(status.selection.map((mapName) => [mapName, []]))

  Object.entries(status.votes).forEach(([player, mapName]) => {
    selection.get(mapName).push(player)
  });

  selection = [...selection]
  selection.sort((a, b) => b[1].length - a[1].length)
  
  return selection;
};

export const VotemapStatus = ({ status }) => {
  const selection = simplifyStatusResult(status)

  return (
    <Wrapper>
      <FormCard fullWidth>
        <Stack direction="row" gap={1} alignItems={'center'} flexWrap={'wrap'}>
          <Typography variant="h6">Current Map Vote</Typography>
          <Box sx={{ flexGrow: 1 }}></Box>
          <Form method="post">
            <Button
              size="small"
              variant="contained"
              name="intent"
              value="reset_votemap_state"
              type="submit"
              color="warning"
            >
              New Selection
            </Button>
          </Form>
        </Stack>
      </FormCard>
      <TableContainer>
        <Table aria-label="Votemap selection result">
          <TableHead>
            <TableRow>
              <TableCell sx={{ maxWidth: 25 }}>Votes</TableCell>
              <TableCell colSpan={3} sx={{ textAlign: 'center' }}>Map</TableCell>
              <TableCell sx={{ textAlign: 'right' }}>Voters</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {selection.length ? (
              selection.map(([map, votes]) => (
                <TableRow>
                  <TableCell sx={{ maxWidth: 25 }}>{votes.length}</TableCell>
                  <TableCell sx={{ maxWidth: 50 }}><Avatar alt={map} src={getMapImageUrl(map)} variant='square' /></TableCell>
                  <TableCell sx={{ maxWidth: 50 }}>{getMapName(map)}</TableCell>
                  <TableCell sx={{ maxWidth: 25 }}>{'mode'}</TableCell>
                  <TableCell sx={{ textAlign: 'right' }}>
                    {votes.join(', ')}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell>-</TableCell>
                <TableCell>No selection</TableCell>
                <TableCell sx={{ textAlign: 'right' }}>-</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Wrapper>
  );
};
