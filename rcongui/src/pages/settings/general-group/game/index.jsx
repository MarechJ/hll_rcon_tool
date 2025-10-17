import React from "react";
import { Divider, Grid2 as Grid, Stack, Typography } from "@mui/material";
import { useLoaderData } from "react-router-dom";
import { DynamicWeatherSettings, SliderTimer } from "../components";
import { cmd } from "@/utils/fetchUtils";
import SelfImprovementIcon from "@mui/icons-material/SelfImprovement";
import TimerIcon from "@mui/icons-material/Timer";
import CloudIcon from "@mui/icons-material/Cloud";

function GameTimersSettings() {
  const loaderData = useLoaderData();

  return (
    <Stack gap={2}>
      <Divider>Dynamic Weather</Divider>
      <Grid container spacing={1}>
        <DynamicWeatherSettings
          options={loaderData.maps}
          settingKey={`map_name`}
          title={`Dynamic Weather Toggle`}
          subheader="Enable or Disable Dynamic Weather for a specific map."
          icon={CloudIcon}
          mutationFn={cmd.SET_DYNAMIC_WEATHER_ENABLED}
        />
      </Grid>
      <Divider>Match Timers</Divider>
      <Grid container spacing={1}>
        {Object.keys(loaderData.timers.match).map((gameMode) => (
          <SliderTimer
            key={`match_${gameMode}_timer`}
            settingKey={`match_${gameMode}_timer`}
            gameMode={gameMode}
            title={`${
              gameMode[0].toUpperCase() + gameMode.slice(1)
            } Match Timer`}
            subheader={gameMode === "offensive" ? "The length of each control point phase." : "The total length of the match."}
            icon={TimerIcon}
            setTimer={cmd.SET_MATCH_TIMER}
            removeTimer={cmd.REMOVE_MATCH_TIMER}
            initialData={loaderData.timers.match[gameMode].default}
          />
        ))}
      </Grid>
      <Divider>Warm Up Timers</Divider>
      <Grid container spacing={1}>
        {Object.keys(loaderData.timers.warmup).map((gameMode) => (
          <SliderTimer
            key={`warmup_${gameMode}_timer`}
            settingKey={`warmup_${gameMode}_timer`}
            gameMode={gameMode}
            title={`${
              gameMode[0].toUpperCase() + gameMode.slice(1)
            } Warm Up Timer`}
            subheader="The length of the match warm up."
            icon={SelfImprovementIcon}
            setTimer={cmd.SET_WARMUP_TIMER}
            removeTimer={cmd.REMOVE_WARMUP_TIMER}
            initialData={loaderData.timers.warmup[gameMode].default}
          />
        ))}
      </Grid>
      <Typography variant="body2" color="text.secondary" component="div">
        <em>{`Example: Match Timer = 93 minutes, Warm Up Timer = 3 minutes => Total Match Time = 93 minutes.`}</em>
      </Typography>
      <Typography variant="body2" color="text.secondary" component="div">
        <em>Note: The changes will be applied on a map change.</em>
      </Typography>
      <Typography variant="body2" color="text.secondary" component="div">
        <em>Note: Removing the timer will set the timer to its default value and the label from the HLL server browser will be removed as well.</em>
      </Typography>
    </Stack>
  );
}

export default GameTimersSettings;
