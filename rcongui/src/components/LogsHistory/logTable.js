import React from "react";
import Link from "@material-ui/core/Link";
import moment from "moment";
import { Grid } from "@material-ui/core";

import MUIDataTable from "mui-datatables";

export default function LogsTable({ logs, downloadCSV }) {
  const [myRowPerPage, setRowPerPage] = React.useState(
    window.localStorage.getItem("logs_row_per_page") || 50
  );
  const saveRowsPerPage = (rowPerPage) => {
    window.localStorage.setItem("logs_row_per_page", rowPerPage);
    setRowPerPage(rowPerPage);
  };
  const columns = [
    {
      name: "event_time",
      label: "Time",
      options: {
        customBodyRenderLite: (dataIndex) =>
          moment
            .unix(logs[dataIndex].event_time)
            .local()
            .format("ddd Do MMM HH:mm:ss"),
      },
    },
    { name: "type", label: "Type" },
    { name: "content", label: "Content" },
    {
      name: "player1_id",
      label: "Name 1",
      options: {
        customBodyRenderLite: (dataIndex) => {
          let id = logs[dataIndex].player1_id;
          let name = logs[dataIndex].player_name;
          return id ? (
            <Link
              color="inherit"
              target="_blank"
              href={`/api/get_player_profile?player_id=${id}`}
            >
              {name}
            </Link>
          ) : (
            name
          );
        },
      },
    },
    {
      name: "player2_id",
      label: "Name 2",
      options: {
        customBodyRenderLite: (dataIndex) => {
          let id = logs[dataIndex].player2_id;
          let name = logs[dataIndex].player2_name;
          return id ? (
            <Link
              color="inherit"
              target="_blank"
              href={`/api/get_player_profile?player_id=${id}`}
            >
              {name}
            </Link>
          ) : (
            name
          );
        },
      },
    },
    { name: "server", label: "Server" },
  ];

  const options = {
    filter: false,
    rowsPerPage: myRowPerPage,
    selectableRows: "none",
    rowsPerPageOptions: [10, 25, 50, 100, 250, 500, 1000],
    onChangeRowsPerPage: saveRowsPerPage,
    onDownload: () => {
      downloadCSV().bind(this);
      return false;
    },
  };

  return (
    <Grid container justify="center">
      <Grid item>
        <MUIDataTable
          title={"Game logs"}
          data={logs}
          columns={columns}
          options={options}
        />
      </Grid>
    </Grid>
  );
}
