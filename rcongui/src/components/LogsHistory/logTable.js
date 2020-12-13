import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import { Link } from 'react-router-dom';
import moment from 'moment'

const useStyles = makeStyles({
  table: {
    minWidth: 650,
  },
});


export default function LogsTable({logs}) {
  const classes = useStyles();

  return (
    <TableContainer component={Paper}>
      <Table className={classes.table} size="small" aria-label="a dense table">
        <TableHead>
          <TableRow>
            <TableCell>Time</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Log</TableCell>
            <TableCell>Name 1</TableCell>
            <TableCell>Name 2</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {logs.map((row) => (
            <TableRow key={row.id}>
              <TableCell>{moment.unix(row.event_time).format("MM/DD/YYYY HH:mm:ss")}</TableCell>
              <TableCell>{row.type}</TableCell>
              <TableCell>{row.content}</TableCell>
              <TableCell>{row.player1_id ? <Link target="_blank" href={`/api/get_player?id=${row.player1_id}`}>{row.player_name}</Link> : row.player_name}</TableCell>
              <TableCell>{row.player2_id ? <Link target="_blank" href={`/api/get_player?id=${row.player2_id}`}>{row.player2_name}</Link> : row.player2_name}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
