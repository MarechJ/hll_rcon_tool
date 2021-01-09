import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import Link from '@material-ui/core/Link';
import moment from 'moment'
import { DataGrid } from '@material-ui/data-grid';
import { Grid } from '@material-ui/core';

import MUIDataTable from "mui-datatables";



export default function LogsTable({ logs }) {
  const columns = [
    {
      name: 'event_time', label: 'Time', options: {
        customBodyRenderLite: (dataIndex) => (moment.unix(logs[dataIndex].event_time).format("ddd Do MMM HH:mm:ss"))
      }
    },
    { name: 'type', label: 'Type', },
    { name: 'content', label: 'Content', },
    {
      name: 'player1_id', label: 'Name 1', options: {
        customBodyRenderLite: (dataIndex) => {
          let id = logs[dataIndex].player1_id;
          let name = logs[dataIndex].player_name;
          return id ? <Link color="inherit" target="_blank" href={`/api/player?id=${id}`}>{name}</Link> : name
        }
      }
    },
    {
      name: 'player2_id', label: 'Name 2', options: {
        customBodyRenderLite: (dataIndex) => {
          let id = logs[dataIndex].player2_id;
          let name = logs[dataIndex].player2_name;
          return id ? <Link color="inherit" target="_blank" href={`/api/player?id=${id}`}>{name}</Link> : name
        }
      }
    },
    { name: 'server', label: 'Server', },
  ];

  const options = {
    filter: false,
    rowsPerPage: 100,
    selectableRows: "none",
  };

  return (
    <Grid container justify="center">
      <Grid item >

        <MUIDataTable
          title={"Game logs"}
          data={logs}
          columns={columns}
          options={options}
        />

      </Grid>
    </Grid>
    // <DataGrid style={{height: "500px"}} rows={logs} columns={[
    //   { name: 'event_time', label: 'Time', },
    //   { name: 'type', label: 'Type', },
    //   { name: 'content', label: 'Content', width: 800 },
    //   { name: 'player1_id', label: 'Name 1', },
    //   { name: 'player2_id', label: 'Name 2', },
    //   { name: 'server', label: 'Server', width: 100 },
    // ]} />
    // <TableContainer component={Paper}>
    //   <Table className={classes.table} size="small" aria-label="a dense table">
    //     <TableHead>
    //       <TableRow>
    //         <TableCell>Time</TableCell>
    //         <TableCell>Type</TableCell>
    //         <TableCell>Log</TableCell>
    //         <TableCell>Name 1</TableCell>
    //         <TableCell>Name 2</TableCell>
    //         <TableCell>Server</TableCell>
    //       </TableRow>
    //     </TableHead>
    //     <TableBody>
    //       {logs.map((row) => (
    //         <TableRow key={row.id}>
    //           <TableCell>{moment.unix(row.event_time).format("ddd Do MMM HH:mm:ss")}</TableCell>
    //           <TableCell>{row.type}</TableCell>
    //           <TableCell>{row.content}</TableCell>
    //           <TableCell>{row.player1_id ? <Link color="inherit" target="_blank" href={`/api/player?id=${row.player2_id}`}>{row.player_name}</Link> : row.player_name}</TableCell>
    //           <TableCell>{row.player2_id ? <Link color="inherit" target="_blank" href={`/api/player?id=${row.player2_id}`}>{row.player2_name}</Link> : row.player2_name}</TableCell>
    //           <TableCell>{row.server}</TableCell>
    //         </TableRow>
    //       ))}
    //     </TableBody>
    //   </Table>
    // </TableContainer>
  );
}
