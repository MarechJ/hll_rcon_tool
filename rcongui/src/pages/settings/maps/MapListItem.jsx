import {
  Box,
  Button,
  IconButton,
  Tooltip,
  Typography,
  Popover,
  Stack,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { MapDetailsCard } from "./MapDetailsCard";
import { useState } from "react";
import VisibilityIcon from "@mui/icons-material/Visibility";

function MapListItemBase({ mapLayer, renderActions }) {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        p: 0.5,
        mb: 1,
        borderRadius: 1,
        border: "1px solid",
        borderColor: "divider",
        "&:hover": { bgcolor: "action.hover" },
      }}
    >
      <MapDetailsCard mapLayer={mapLayer} />
      {renderActions && (
        <Box sx={{ display: "flex", gap: 1 }}>{renderActions(mapLayer)}</Box>
      )}
    </Box>
  );
}

export function MapListItem({ mapLayer }) {
  return <MapListItemBase mapLayer={mapLayer} />;
}

export function MapChangeListItem({ mapLayer, onClick }) {
  return (
    <MapListItemBase
      mapLayer={mapLayer}
      renderActions={(mapLayer) => (
        <Tooltip title="Set as current map">
          <span>
            <IconButton
              sx={{
                borderRadius: 0,
                bgcolor: "primary.main",
                color: "primary.contrastText",
                "&:hover": {
                  bgcolor: "primary.dark",
                },
              }}
              size="small"
              onClick={() => onClick(mapLayer)}
            >
              <PlayArrowIcon />
            </IconButton>
          </span>
        </Tooltip>
      )}
    />
  );
}

export function MapBuilderListItem({ mapLayer, onClick }) {
  return (
    <MapListItemBase
      mapLayer={mapLayer}
      renderActions={(mapLayer) => (
        <Button
          variant="contained"
          size="small"
          startIcon={<AddIcon />}
          onClick={() => onClick(mapLayer)}
        >
          Add
        </Button>
      )}
    />
  );
}

export function MapVotemapListItem({ mapLayer, voters }) {
  const [anchorEl, setAnchorEl] = useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? `${mapLayer.id}-voters` : undefined;

  return (
    <MapListItemBase
      mapLayer={mapLayer}
      renderActions={() => (
        <Stack sx={{ px: 1 }} alignItems={"center"} direction={"row"} spacing={2}>
          <Box sx={{}}>{`Votes: ${voters.length}`}</Box>
          <Button
            aria-describedby={id}
            onClick={handleClick}
          >
            Show
          </Button>
          <Popover
            id={id}
            open={open}
            anchorEl={anchorEl}
            onClose={handleClose}
            anchorOrigin={{
              vertical: "top",
              horizontal: "left",
            }}
            transformOrigin={{
              vertical: "bottom",
              horizontal: "right",
            }}
          >
            <Box>
              {voters.map((voter, i) => (
                <Box sx={{ py: 1, px: 2 }} key={voter + i}>{voter}</Box>
              ))}
            </Box>
          </Popover>
        </Stack>
      )}
    />
  );
}
