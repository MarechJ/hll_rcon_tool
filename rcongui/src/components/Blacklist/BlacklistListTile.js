import {
  Grid,
  IconButton,
  InputLabel,
  Paper,
  Tooltip,
  Typography,
} from "@mui/material";
import React from "react";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import { SYNC_METHODS } from "./BlacklistListCreateDialog";

const BlacklistListTile = ({
  blacklist,
  servers,
  onEdit,
  onDelete,
}) => {

  function serverNumberToName(serverNumber) {
    return servers[serverNumber] || serverNumber.toString();
  }

  return (
    (<Paper>
      <Grid container
        justifyContent="space-between"
        alignItems="center"
        spacing={2}
        style={{paddingLeft: 18}}
      >
        <Grid item>
          <Typography variant="h6" color="textSecondary">#{blacklist.id}</Typography>
        </Grid>
        <Grid item xs={2}>
          <InputLabel align="left">Blacklist Name</InputLabel>
          <Typography align="left">
            {blacklist.name}
          </Typography>
        </Grid>

        <Grid item xs={6}>
          <InputLabel align="left">Servers</InputLabel>
          {
            blacklist.servers === null
            ? <Typography align="left">All</Typography>
            : blacklist.servers.length === 0
            ? <Typography align="left">None</Typography>
            : <React.Fragment>
              {blacklist.servers.map((num) => (
                <Typography key={num} align="left" noWrap>
                  {serverNumberToName(num)}
                </Typography>
              ))}
            </React.Fragment>
          }
        </Grid>
        
        <Grid item xs={2}>
          <InputLabel align="left">Sync Method</InputLabel>
          <Typography align="left">{SYNC_METHODS[blacklist.sync]}</Typography>
        </Grid>
        
        <Grid item>
          <Tooltip title="Edit">
            <IconButton onClick={() => onEdit(blacklist)} size="large">
              <EditIcon/>
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <span>
              <IconButton onClick={() => onDelete(blacklist)} disabled={blacklist.id === 0}>
                <DeleteIcon/>
              </IconButton>
            </span>
          </Tooltip>
        </Grid>
      </Grid>
    </Paper>)
  );
}

export default BlacklistListTile;
