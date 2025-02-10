import {
  IconButton,
  InputLabel,
  Paper,
  Tooltip,
  Typography,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import { SYNC_METHODS } from "./VipListListCreateDialog";
import Grid from "@mui/material/Grid2";
import { Fragment } from "react";


const VipListListTile = ({
  vipList,
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
        style={{ paddingLeft: 18 }}
      >
        <Grid>
          <Typography variant="h6" color="textSecondary">#{vipList.id}</Typography>
        </Grid>
        <Grid size={2}>
          <InputLabel align="left">VIP List Name</InputLabel>
          <Typography align="left">
            {vipList.name}
          </Typography>
        </Grid>

        <Grid size={6}>
          <InputLabel align="left">Servers</InputLabel>
          {
            vipList.servers === null
              ? <Typography align="left">All</Typography>
              : vipList.servers.length === 0
                ? <Typography align="left">None</Typography>
                : <Fragment>
                  {vipList.servers.map((num) => (
                    <Typography key={num} align="left" noWrap>
                      {serverNumberToName(num)}
                    </Typography>
                  ))}
                </Fragment>
          }
        </Grid>

        <Grid size={2}>
          <InputLabel align="left">Sync Method</InputLabel>
          <Typography align="left">{SYNC_METHODS[vipList.sync]}</Typography>
        </Grid>

        <Grid>
          <Tooltip title="Edit">
            <IconButton onClick={() => onEdit(vipList)} size="large">
              <EditIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <span>
              <IconButton
                onClick={() => onDelete(vipList)}
                disabled={vipList.id === 0}
                size="large">
                <DeleteIcon />
              </IconButton>
            </span>
          </Tooltip>
        </Grid>
      </Grid>
    </Paper>)
  );
}

export default VipListListTile;
