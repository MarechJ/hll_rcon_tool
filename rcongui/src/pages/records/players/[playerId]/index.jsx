import {
  get,
  execute,
} from "@/utils/fetchUtils";
import { Avatar, Box, Button, Link, Popover, Stack } from "@mui/material";
import Typography from "@mui/material/Typography";
import { ExpandMore } from "@mui/icons-material";
import { ChatContent } from "@/components/ChatWidget";
import MessageHistory from "@/components/MessageHistory";
import { toast } from "react-toastify";
import { defer, useLoaderData, useSubmit } from "react-router-dom";
import CollapseCard from "@/components/collapseCard";
import makePlayerProfileUrl from "@/utils/makePlayerProfileUrl";
import Grid from "@mui/material/Grid2";
import { DataGrid, GridToolbar } from "@mui/x-data-grid";
import dayjs from "dayjs";
import { useState } from "react";

const fetchResource = async (url, errorMessage) => {
  try {
    const response = await get(url);
    if (!response.ok) throw new Response(errorMessage, { status: 404 });
    const data = await response.json();
    if (!data.result) throw new Response(errorMessage, { status: 404 });
    return data.result;
  } catch (error) {
    console.warn(`Failed to fetch ${url}:`, error);
    return null; // Return null if any request fails
  }
};

export const loader = async ({ params }) => {
  const { playerId } = params;

  // Use the fetchResource function for each API call
  const fetchPlayer = fetchResource(
    `get_player_profile?player_id=${playerId}`,
    "Player not found"
  );

  const fetchMessages = fetchResource(
    `get_player_messages?player_id=${playerId}`,
    "Messages not found"
  );

  const fetchConnectionInfo = fetchResource(
    "get_connection_info",
    "Connection info not found"
  );

  // Run all promises concurrently
  const [profile, messages, connectionInfo] = await Promise.all([
    fetchPlayer,
    fetchMessages,
    fetchConnectionInfo,
  ]);

  // If player is not found, throw an error
  if (!profile) {
    throw new Response("Player not found", { status: 404 });
  }

  // Return a deferred object to allow data to load in parallel
  return defer({
    profile,
    messages,
    connectionInfo,
  });
};

export const action = async ({ request }) => {
  let formData = await request.formData();

  try {
    const res = await execute(
      'post_player_comment',
      {
        player_id: formData.get("player_id"),
        comment: formData.get("comment"),
      }
    );
    if (!res.ok) throw res;
  } catch (error) {
    toast.error('Failed to save the comment.')
    return { ok: false, error }
  }
  return { ok: true };
}

const columns = [
  {
    field: "time",
    headerName: "Time",
    width: 160,
    valueFormatter: (value) => dayjs(value).format("lll"),
  },
  {
    field: "action_type",
    headerName: "Type",
    width: 120,
  },
  { field: "by", headerName: "Initiator", width: 120 },
  { field: "reason", headerName: "Reason", flex: 1, sortable: false },
];

// return a label for steam and windows ids types
const getLinkLabel = (id) => {
  if (id.length === 17) {
    // valid steam id is 17 digits...
    return "Steam";
  } else {
    // xbox gamertags are unique and cost $$ to change...
    // otherwise assume it's a T17 guid and return
    // a url to https://xboxgamertag.com/search/ name
    return "xboxgamertag.com";
  }
};

const NamePopOver = ({ names }) => {
  const [anchorEl, setAnchorEl] = useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? "name-popover" : undefined;
  // TODO replace with a List with sublist so that on can copy past the names, also see at what time it was created + last seen
  return (
    <Grid>
      <Button endIcon={<ExpandMore />} onClick={handleClick}>
        <Typography variant="h3">
          {names.length ? names[0].name : "Player has no recorded names"}
        </Typography>
      </Button>
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "center",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "center",
        }}
      >
        <Grid container>
          {names.map((name) => {
            return (
              <Grid key={name} size={12}>
                <Typography variant="body2">{name.name}</Typography>
              </Grid>
            );
          })}
        </Grid>
      </Popover>
    </Grid>
  );
};

const Punishment = ({ punishments }) => {
  return (
    <DataGrid
      rows={punishments}
      columns={columns}
      initialState={{
        pagination: {
          paginationModel: {
            pageSize: 100,
          },
        },
        density: "compact",
      }}
      pageSizeOptions={[10, 25, 50, 100]}
      slots={{ toolbar: GridToolbar }}
      disableRowSelectionOnClick
      getRowId={(row) => row.time + row.action_type}
    />
  );
};

const Is = ({ bool, text }) =>
  bool ? (
    <Grid>
      <Typography color="secondary" variant="button">
        {text}
      </Typography>
    </Grid>
  ) : (
    ""
  );

const PlayerInfo = () => {
  const { profile, messages, connectionInfo } = useLoaderData();
  const submit = useSubmit()

  const {
    player_id,
    names,
    sessions,
    total_playtime_seconds,
    received_actions,
    penalty_count,
    is_blacklisted,
    steaminfo,
    vips,
    bans,
    comments,
  } = profile;

  const hasTempBan = !!bans.find((ban) => {
    return ban.type === "temp";
  });

  const hasPermaBan = !!bans.find((ban) => {
    return ban.type === "perma";
  });

  // const hasVip = vips.some(
  //   (vip) => vip.server_number === connectionInfo?.server_number
  // );

  const handleSubmitComment = (comment) => {
    let formData = new FormData();
    formData.append("player_id", player_id);
    formData.append("comment", comment);
    submit(formData, { method: 'POST' });
  };

  return (
    <Stack spacing={2}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={{ xs: 1, sm: 2, md: 4 }}
        sx={{ width: "100%" }}
      >
        <Box>
          <Avatar
            style={{
              height: "150px",
              width: "150px",
              fontSize: "5rem",
            }}
            variant="square"
            src={steaminfo?.profile?.avatarfull}
          >
            {names[0]?.name[0].toUpperCase()}
          </Avatar>
          <NamePopOver names={names} />
          <div>
            {[
              // [hasVip, "VIP"],
              [is_blacklisted, "IS BLACKLISTED"],
              [hasPermaBan, "IS PERMABANNED"],
              [hasTempBan, "IS TEMPBANNED"],
            ].map((e) => (
              <Is key={e[1]} bool={e[0]} text={e[1]} />
            ))}
          </div>
          <Typography variant="h6">
            <Link href={makePlayerProfileUrl(player_id, names[0]?.name)}>
              {getLinkLabel(player_id)} Profile
            </Link>
          </Typography>
          <Typography variant="h6">Last connection</Typography>
          <Typography>
            {dayjs(sessions[0]?.end || sessions[0]?.start).format(
              "ddd Do MMM HH:mm:ss"
            )}
          </Typography>
          <Typography variant="h6">Total play time</Typography>
          <Typography>
            {dayjs.duration(total_playtime_seconds, "seconds").humanize()}
          </Typography>
          <Typography variant="h6">Player penalties</Typography>
          <Typography>Perma ban: {penalty_count.PERMABAN}</Typography>
          <Typography>Temp ban: {penalty_count.TEMPBAN}</Typography>
          <Typography>Kick: {penalty_count.KICK}</Typography>
          <Typography>Punish: {penalty_count.PUNISH}</Typography>
          <Typography variant="h6">
            <Link
              href={`${process.env.REACT_APP_API_URL}get_player_profile?player_id=${player_id}`}
            >
              Raw profile
            </Link>
          </Typography>
        </Box>
        <Box sx={{ flexGrow: 1 }}>
          <Punishment punishments={received_actions} />
        </Box>
      </Stack>
      <Stack spacing={2}>
        <CollapseCard title="Comments" startOpen>
          <ChatContent data={comments} handleMessageSend={handleSubmitComment} />
        </CollapseCard>
        <CollapseCard title="Message History" startOpen>
          <MessageHistory data={messages} />
        </CollapseCard>
      </Stack>
    </Stack>
  );
};

export default PlayerInfo;
