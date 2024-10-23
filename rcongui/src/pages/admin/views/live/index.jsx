import React from "react";
import Grid from "@mui/material/Grid2";
import PlayerView from "@/components/PlayerView";
import GameLogs from "@/components/LiveLogs";
import { cmd, execute, get, handleHttpError } from "@/utils/fetchUtils";
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
import { useLoaderData } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
// import teamViewResponse from "./data.json"

export const StyledToggleButtonGroup = styled(ToggleButtonGroup)(
  ({ theme }) => ({
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
  })
);

export function CustomizedDividers() {
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
        <Box sx={{ p: "10px", display: "grid", alignItems: "center" }}>
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
  const logs = await cmd.GET_LIVE_LOGS({
    params: {
      end: 100,
      filter_action: [],
      filter_player: [],
      inclusive_filter: true,
    },
  });

  return { initialLogsView: logs };
};

const Live = () => {
  const { initialLogsView } = useLoaderData();

  const { data: teamData } = useQuery({
    queryKey: ["teams", "live"],
    queryFn: cmd.GET_LIVE_TEAMS,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  // const teamData = teamViewResponse.result;

  const { data: gameState } = useQuery({
    queryKey: ["game", "state"],
    queryFn: cmd.GET_GAME_STATE,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  const rows = React.useMemo(() => {
    if (!teamData) return [];
    const players = extractPlayers(teamData);
    return players.map(playerToRow);
  }, [teamData]);

  const gameStateProp = React.useMemo(() => {
    if (gameState && teamData) {
      return {
        ...gameState,
        allies: extractTeamState(teamData?.allies ?? {}),
        axis: extractTeamState(teamData?.axis ?? {}),
      };
    }
    return null;
  }, [gameState, teamData]);

  return (
    <Grid container spacing={1}>
      <Grid size={12}>
        <Header teamData={teamData} gameState={gameStateProp} />
      </Grid>
      <Grid
        size={{
          sm: 12,
          lg: "auto",
        }}
      >
        <PlayersTable columns={columns} rows={rows} data={teamData ?? {}} />
      </Grid>
      <Grid
        size={{
          sm: 12,
          lg: "grow",
        }}
      >
        <GameLogs initialLogsView={initialLogsView} />
      </Grid>
    </Grid>
  );
};

export default Live;
