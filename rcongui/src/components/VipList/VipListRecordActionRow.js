import { ButtonGroup, Button } from "@mui/material";
import Tooltip from "@mui/material/Tooltip";
import EditIcon from "@mui/icons-material/Edit";
import TimerOffIcon from "@mui/icons-material/TimerOff";
import StarIcon from '@mui/icons-material/Star';
import DeleteIcon from "@mui/icons-material/Delete";
import Grid from "@mui/material/Grid2";


const VipListRecordActionRow = ({
  isExpired: isActive,
  onEdit,
  onActivate,
  onInactivate,
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

          {isActive ? <Button>
            <Tooltip title="Inactivate this record" arrow>
              <TimerOffIcon size="small" onClick={onInactivate} />
            </Tooltip>
          </Button> : <Button>
            <Tooltip title="Activate this record" arrow>
              <StarIcon size="small" onClick={onActivate} />
            </Tooltip>
          </Button>}


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

export default VipListRecordActionRow;
