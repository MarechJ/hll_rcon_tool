import React from "react";
import { Grid2 as Grid } from "@mui/material";
import BalanceIcon from "@mui/icons-material/Balance";
import GavelIcon from "@mui/icons-material/Gavel";
import TimerIcon from "@mui/icons-material/Timer";
import NetworkPingIcon from "@mui/icons-material/NetworkPing";
import QueueIcon from "@mui/icons-material/Queue";
import StarIcon from "@mui/icons-material/Star";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import HowToVoteIcon from "@mui/icons-material/HowToVote";
import RuleIcon from "@mui/icons-material/Rule";
import { cmd } from "@/utils/fetchUtils";
import { useLoaderData } from "react-router-dom";
import {
  AutoVotekickSetting,
  GENERAL_KEY,
  SliderSetting,
  ThresholdsSetting,
  ToggleSetting,
} from "../components";

function GeneralSettings() {
  const loaderData = useLoaderData();

  return (
    <Grid container spacing={1}>
      <SliderSetting
        settingKey={GENERAL_KEY.team_switch_cooldown}
        payloadKey={"minutes"}
        title="Team Switch Cooldown"
        subheader="Time players must wait before switching teams"
        icon={TimerIcon}
        queryKey={{ queryIdentifier: "get_server_settings" }}
        mutationFn={cmd.SET_TEAM_SWITCH_COOLDOWN}
        initialData={loaderData.settings}
      />

      <SliderSetting
        settingKey={GENERAL_KEY.max_ping_autokick}
        payloadKey={"max_ms"}
        title="Max Ping Autokick"
        subheader="Maximum ping allowed before auto-kicking players"
        icon={NetworkPingIcon}
        queryKey={{ queryIdentifier: "get_server_settings" }}
        mutationFn={cmd.SET_MAX_PING_AUTOKICK}
        initialData={loaderData.settings}
      />

      <SliderSetting
        settingKey={GENERAL_KEY.queue_length}
        payloadKey={"value"}
        title="Queue Length"
        subheader="Maximum number of players in queue"
        icon={QueueIcon}
        queryKey={{ queryIdentifier: "get_server_settings" }}
        mutationFn={cmd.SET_QUEUE_LENGTH}
        initialData={loaderData.settings}
      />

      <SliderSetting
        settingKey={GENERAL_KEY.vip_slots_num}
        payloadKey={"value"}
        title="VIP Slots"
        subheader="Number of reserved slots for VIP players"
        icon={StarIcon}
        queryKey={{ queryIdentifier: "get_server_settings" }}
        mutationFn={cmd.SET_VIP_SLOTS_NUM}
        initialData={loaderData.settings}
      />

      <ToggleSetting
        settingKey={GENERAL_KEY.autobalance_enabled}
        payloadKey={"value"}
        title="Autobalance"
        subheader="Enable automatic team balancing"
        icon={BalanceIcon}
        queryKey={{ queryIdentifier: "get_server_settings" }}
        mutationFn={cmd.SET_AUTOBALANCE_ENABLED}
        initialData={loaderData.settings}
      />

      <SliderSetting
        settingKey={GENERAL_KEY.autobalance_threshold}
        payloadKey={"max_diff"}
        title="Autobalance Threshold"
        subheader="Maximum team size difference before balancing"
        icon={BalanceIcon}
        queryKey={{ queryIdentifier: "get_server_settings" }}
        mutationFn={cmd.SET_AUTOBALANCE_THRESHOLD}
        initialData={loaderData.settings}
      />

      <SliderSetting
        settingKey={GENERAL_KEY.idle_autokick_time}
        payloadKey={"minutes"}
        title="Idle Autokick Time"
        subheader="Time before idle players are auto-kicked"
        icon={AccessTimeIcon}
        queryKey={{ queryIdentifier: "get_server_settings" }}
        mutationFn={cmd.SET_IDLE_AUTOKICK_TIME}
        initialData={loaderData.settings}
      />

      <ToggleSetting
        settingKey={GENERAL_KEY.votekick_enabled}
        payloadKey={"value"}
        title="Votekick"
        subheader="Enable player voting to kick other players"
        icon={HowToVoteIcon}
        queryKey={{ queryIdentifier: "get_server_settings" }}
        mutationFn={cmd.SET_VOTEKICK_ENABLED}
        initialData={loaderData.settings}
      />

      <ThresholdsSetting
        settingKey={GENERAL_KEY.votekick_thresholds}
        payloadKey={"threshold_pairs"}
        title="Votekick Thresholds"
        subheader="Vote requirements based on player count"
        icon={RuleIcon}
        queryKey={{ queryIdentifier: "get_server_settings" }}
        mutationFn={cmd.SET_VOTEKICK_THRESHOLDS}
        initialData={loaderData.settings}
      />

      <AutoVotekickSetting
        title="Auto Votekick Settings"
        subheader="Automatically toggle votekick based on moderator availability"
        icon={GavelIcon}
        queryKey={{ queryIdentifier: "get_votekick_autotoggle_config" }}
        mutationFn={cmd.SET_VOTEKICK_AUTOTOGGLE_CONFIG}
        initialData={loaderData.autokickSettings}
      />
    </Grid>
  );
}

export default GeneralSettings;
