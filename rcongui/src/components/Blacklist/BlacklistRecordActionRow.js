import { ButtonGroup, Button, Grid } from "@material-ui/core";
import React from "react";
import Tooltip from "@material-ui/core/Tooltip";
import EditIcon from "@material-ui/icons/Edit";
import TimerOffIcon from "@material-ui/icons/TimerOff";
import DeleteIcon from "@material-ui/icons/Delete";

const BlacklistRecordActionRow = ({
  isExpired,
  onEdit,
  onExpire,
  onDelete,
}) => {
  return (
    <Grid container justify="center">
      <Grid item>
        <ButtonGroup size="small" variant="text">
          <Button>
            <Tooltip
              title="Edit this record"
              arrow
            >
              <EditIcon size="small" onClick={onEdit} />
            </Tooltip>
          </Button>

          <Button disabled={isExpired}>
            <Tooltip title="Expire this record" arrow>
              <TimerOffIcon size="small" onClick={onExpire} />
            </Tooltip>
          </Button>

          <Button>
            <Tooltip title="Delete this record" arrow>
              <DeleteIcon size="small" onClick={onDelete} />
            </Tooltip>
          </Button>
        </ButtonGroup>
      </Grid>
    </Grid>
  );
};

export default BlacklistRecordActionRow;