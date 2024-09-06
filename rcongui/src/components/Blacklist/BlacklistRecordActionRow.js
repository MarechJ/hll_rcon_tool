import { ButtonGroup, Button } from "@mui/material";
import React from "react";
import Tooltip from "@mui/material/Tooltip";
import EditIcon from "@mui/icons-material/Edit";
import TimerOffIcon from "@mui/icons-material/TimerOff";
import DeleteIcon from "@mui/icons-material/Delete";
import Grid from "@mui/material/Grid2";


const BlacklistRecordActionRow = ({
  isExpired,
  onEdit,
  onExpire,
  onDelete,
}) => {
  return (
    (<Grid container justifyContent="center">
      <Grid>
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
    </Grid>)
  );
};

export default BlacklistRecordActionRow;