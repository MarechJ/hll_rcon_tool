import {
  Box,
  Button,
  IconButton,
  Tooltip,
  Popover,
  Stack,
  Typography,
  Divider,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import { MapDetailsCard } from "./MapDetailsCard";
import { useState } from "react";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import CloseIcon from "@mui/icons-material/Close";
import VisibilityIcon from "@mui/icons-material/Visibility";
import { PlayerDrawerLink } from "@/components/shared/PlayerDrawerLink";

function MapListItemBase({ mapLayer, renderActions, sx, ...props }) {
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
        ...sx,
      }}
      {...props}
    >
      <MapDetailsCard mapLayer={mapLayer} />
      {renderActions && <>{renderActions(mapLayer)}</>}
    </Box>
  );
}

export function MapListItem({ mapLayer }) {
  return <MapListItemBase mapLayer={mapLayer} />;
}

export function MapChangeListItem({ mapLayer, onClick, icon, title }) {
  return (
    <MapListItemBase
      mapLayer={mapLayer}
      renderActions={(mapLayer) => (
        <Tooltip title={title ?? "Set as current map"}>
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
              {icon ?? <PlayArrowIcon />}
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

export function MapVotemapListItem({ mapLayer, voters, votesCount, onClick }) {
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
      renderActions={(mapLayer) => (
        <Stack
          direction={"row"}
          justifyContent={"center"}
          alignItems={"center"}
        >
          <Stack>
            <Typography fontSize={"0.75rem"} color="text.secondary">Votes</Typography>
            <Typography textAlign={"center"} fontWeight={500}>
              {votesCount}
            </Typography>
          </Stack>

          <Divider flexItem orientation="vertical" sx={{ px: 0.5, mx: 0.5 }} />

          <Tooltip title="Show voters">
            <IconButton
              aria-describedby={id}
              size="small"
              onClick={handleClick}
            >
              <VisibilityIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Remove from selection">
            <IconButton
              size="small"
              color="error"
              onClick={() => onClick(mapLayer)}
            >
              <CloseIcon />
            </IconButton>
          </Tooltip>
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
                <Box sx={{ py: 1, px: 2 }} key={voter + i}>
                  <PlayerDrawerLink playerId={voter.player_id}>
                    {voter.player_name}: {voter.count}
                  </PlayerDrawerLink>
                </Box>
              ))}
            </Box>
          </Popover>
        </Stack>
      )}
    />
  );
}

export function MapVotemapResultListItem({ mapLayer, votesCount }) {
  return (
    <MapListItemBase
      mapLayer={mapLayer}
      renderActions={() => (
        <Stack>
        <Typography fontSize={"0.75rem"} color="text.secondary">Votes</Typography>
        <Typography textAlign={"center"} fontWeight={500}>
          {votesCount}
        </Typography>
      </Stack>
      )}
    />
  );
}

export function MapVotemapWhitelistItem({ mapLayer, onClick }) {
  return (
    <MapListItemBase
      mapLayer={mapLayer}
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        p: 0.5,
        mb: 1,
        borderRadius: 1,
        border: "1px solid",
        borderColor: "divider",
        boxShadow: 1,
      }}
      renderActions={(mapLayer) => (
        <Tooltip title="Remove from whitelist">
          <IconButton
            size="small"
            color="error"
            onClick={() => onClick(mapLayer)}
          >
            <CloseIcon />
          </IconButton>
        </Tooltip>
      )}
    />
  );
}
