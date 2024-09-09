import React from "react";
import Grid from "@mui/material/Grid2";
import PlayerView from "@/components/PlayerView";
import GameLogs from "@/components/LiveLogs";
import { execute, get, handleHttpError } from "@/utils/fetchUtils";
import { styled } from "@mui/material/styles";
import FormatAlignLeftIcon from "@mui/icons-material/FormatAlignLeft";
import FormatAlignCenterIcon from "@mui/icons-material/FormatAlignCenter";
import FormatAlignRightIcon from "@mui/icons-material/FormatAlignRight";
import FormatAlignJustifyIcon from "@mui/icons-material/FormatAlignJustify";
import FormatBoldIcon from "@mui/icons-material/FormatBold";
import FormatItalicIcon from "@mui/icons-material/FormatItalic";
import FormatUnderlinedIcon from "@mui/icons-material/FormatUnderlined";
import FormatColorFillIcon from "@mui/icons-material/FormatColorFill";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import Divider from "@mui/material/Divider";
import Paper from "@mui/material/Paper";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup, {
  toggleButtonGroupClasses,
} from "@mui/material/ToggleButtonGroup";
import { Box, InputBase } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import PlayersTable, { playerToRow } from "./players-table";
import { columns } from "./columns";
import { useAsyncInterval, useInterval } from "@/hooks/useInterval";
import { Header } from "@/components/game/Header";
import { extractPlayers, extractTeamState } from "@/utils/extractPlayers";

const StyledToggleButtonGroup = styled(ToggleButtonGroup)(({ theme }) => ({
  [`& .${toggleButtonGroupClasses.grouped}`]: {
    margin: theme.spacing(0.5),
    border: 0,
    borderRadius: theme.shape.borderRadius,
    [`&.${toggleButtonGroupClasses.disabled}`]: {
      border: 0,
    },
  },
  [`& .${toggleButtonGroupClasses.middleButton},& .${toggleButtonGroupClasses.lastButton}`]:
    {
      marginLeft: -1,
      borderLeft: "1px solid transparent",
    },
}));

function CustomizedDividers() {
  const [alignment, setAlignment] = React.useState("left");
  const [formats, setFormats] = React.useState(() => ["italic"]);

  const handleFormat = (event, newFormats) => {
    setFormats(newFormats);
  };

  const handleAlignment = (event, newAlignment) => {
    setAlignment(newAlignment);
  };

  return (
    <div>
      <Paper
        elevation={0}
        sx={(theme) => ({
          display: "flex",
          border: `1px solid ${theme.palette.divider}`,
          flexWrap: "wrap",
        })}
      >
        <Box sx={{ p: '10px', display: 'grid', alignItems: 'center' }}>
          <SearchIcon />
        </Box>
        <InputBase
          sx={{ ml: 1, width: 150 }}
          placeholder="Search Player"
          inputProps={{ "aria-label": "search player" }}
        />
        <StyledToggleButtonGroup
          size="small"
          value={alignment}
          exclusive
          onChange={handleAlignment}
          aria-label="text alignment"
        >
          <ToggleButton value="left" aria-label="left aligned">
            <FormatAlignLeftIcon />
          </ToggleButton>
          <ToggleButton value="center" aria-label="centered">
            <FormatAlignCenterIcon />
          </ToggleButton>
          <ToggleButton value="right" aria-label="right aligned">
            <FormatAlignRightIcon />
          </ToggleButton>
          <ToggleButton value="justify" aria-label="justified" disabled>
            <FormatAlignJustifyIcon />
          </ToggleButton>
        </StyledToggleButtonGroup>
        <Divider flexItem orientation="vertical" sx={{ mx: 0.5, my: 1 }} />
        <StyledToggleButtonGroup
          size="small"
          value={formats}
          onChange={handleFormat}
          aria-label="text formatting"
        >
          <ToggleButton value="bold" aria-label="bold">
            <FormatBoldIcon />
          </ToggleButton>
          <ToggleButton value="italic" aria-label="italic">
            <FormatItalicIcon />
          </ToggleButton>
          <ToggleButton value="underlined" aria-label="underlined">
            <FormatUnderlinedIcon />
          </ToggleButton>
          <ToggleButton value="color" aria-label="color" disabled>
            <FormatColorFillIcon />
            <ArrowDropDownIcon />
          </ToggleButton>
        </StyledToggleButtonGroup>
      </Paper>
    </div>
  );
}

export const loader = async () => {
  const response = await execute("get_recent_logs", {
    end: 100,
    filter_action: [],
    filter_player: [],
    inclusive_filter: true,
  });

  handleHttpError(response);

  const data = await response.json();
  const initialLogsView = data.result;

  return { initialLogsView };
};

const interval = 30;

const getTeamView = () => get('get_team_view');
const getGameState = () => get('get_gamestate');

const Live = () => {
  const [mdSize, setMdSize] = React.useState(6);
  const [direction, setDirection] = React.useState("");
  const [open, setOpen] = React.useState(false);
  const { data: teamData } = useAsyncInterval(getTeamView, interval * 1000);
  const { data: gameState } = useAsyncInterval(getGameState, interval * 1000);

  console.log({gameState})

  const gameStateProp = React.useMemo(() => {
    if (gameState && teamData) {
      return {
        ...gameState.result,
        allies: extractTeamState(teamData?.result?.allies ?? {}),
        axis: extractTeamState(teamData?.result?.axis ?? {}),
      };
    }

    return null;
  }, [gameState, teamData]);

  const rows = React.useMemo(() => {
    if (!teamData) return [];
    const players = extractPlayers(teamData.result);
    return players.map(playerToRow)
  }, [teamData]);

  const toggleDrawer = (newOpen) => () => {
    setOpen(newOpen);
  };
  const isFullScreen = () => mdSize !== 6 ? 12 : 6;
  const toggleMdSize = () => (isFullScreen() ? setMdSize(6) : setMdSize(12));

  return (
    <Grid container spacing={1}>
      {/* <Grid size={12}>
        <Header teamData={teamData?.result} gameState={gameStateProp} />
      </Grid> */}
      <Grid
        size={{
          sm: 12,
          md: "auto",
        }}
      >
        <CustomizedDividers />
        <PlayersTable columns={columns} rows={rows} data={teamData ?? {}} />
      </Grid>
      <Grid
        size={{
          sm: 12,
          md: "grow",
        }}
      >
        <GameLogs />
      </Grid>
    </Grid>
  );
};

export default Live;
