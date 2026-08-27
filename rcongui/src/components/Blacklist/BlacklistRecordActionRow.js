import { ButtonGroup, Button } from "@mui/material";
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
    <Grid container justifyContent="center">
      <Grid>
        <ButtonGroup size="small" variant="text">
          <Button>
            <Tooltip title="Edit this record" arrow>
              <EditIcon size="small" onClick={onEdit} />
            </Tooltip>
          </Button>

          <Button color="warning" disabled={isExpired} onClick={onExpire}>
            <Tooltip title="Expire this record" arrow>
              <TimerOffIcon size="small" />
            </Tooltip>
          </Button>

          <Button color="error" onClick={onDelete}>
            <Tooltip title="Delete this record" arrow>
              <DeleteIcon size="small" />
            </Tooltip>
          </Button>
        </ButtonGroup>
      </Grid>
    </Grid>
  );
};

export default BlacklistRecordActionRow;
