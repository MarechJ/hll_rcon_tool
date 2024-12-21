import { cmd } from "@/utils/fetchUtils";
import {
  Button,
  TextField,
  FormControlLabel,
  Switch,
  Stack,
  Grid2 as Grid,
  Divider,
  Chip,
  Popover,
  IconButton,
  Skeleton,
  Typography,
} from "@mui/material";
import { Form, useLoaderData } from "react-router-dom";
import { Autocomplete } from "@mui/material";
import { CountryFlag } from "@/components/shared/CountryFlag";
import { useMemo, useState, Suspense, lazy } from "react";
import countries from "country-list";
import PlayerCard from "./card";
import { useGlobalStore } from "@/hooks/useGlobalState";
import emojiData from "@emoji-mart/data/sets/15/twitter.json";
import Emoji from "@/components/shared/Emoji";
import AddReactionIcon from "@mui/icons-material/AddReaction";
const EmojiPicker = lazy(() => import("@emoji-mart/react"));

// Get all countries for autocomplete
const countryOptions = countries.getCodes().map((code) => ({
  code: code.toLowerCase(),
  name: countries.getName(code),
}));

/*

blacklisted: false
exact_name_match: false
ignore_accent: true
is_watched: false
page: 1
page_size: 50
player_id: "1"
player_name: "a"
flags: "👍,😍"
country: "cs" // ISO format
*/
export const loader = async ({ request }) => {
  const url = new URL(request.url);

  const player_name = url.searchParams.get("player_name") ?? "";
  const player_id = url.searchParams.get("player_id") ?? "";

  const page = url.searchParams.get("page") ?? 1;
  const page_size = url.searchParams.get("page_size") ?? 50;

  const flags = url.searchParams.get("flags") ?? "";
  const country = url.searchParams.get("country") ?? "";

  const blacklisted = url.searchParams.get("blacklisted") ?? false;
  const exact_name_match = url.searchParams.get("exact_name_match") ?? false;
  const ignore_accent = url.searchParams.get("ignore_accent") ?? false;
  const is_watched = url.searchParams.get("is_watched") ?? false;

  // In the background, this command is POST request therefore the payload and not params
  const playersRecords = await cmd.GET_PLAYERS_RECORDS({
    payload: {
      player_id,
      page,
      page_size,
      flags,
      blacklisted,
      exact_name_match,
      ignore_accent,
      is_watched,
      player_name,
      country,
    },
  });

  const bans = await cmd.GET_BANS();

  return {
    players: playersRecords.result.players.map((player) => ({
      ...player,
      is_banned: bans.some((ban) => ban.player_id === player.player_id),
    })),
    total_pages: playersRecords.result.total_pages,
  };
};

export default function PlayersRecords() {
  const { players: playersData } = useLoaderData();
  const server = useGlobalStore((state) => state.serverState);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [selectedEmoji, setSelectedEmoji] = useState([]);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const players = useMemo(() => {
    if (!server) return playersData;
    return playersData.map((player) => ({
      ...player,
      is_vip:
        player.vips &&
        player.vips.some((vip) => vip.server_number === server.server_number),
    }));
  }, [playersData, server]);

  const handleEmojiButtonClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <div>
      <h1>Players Records</h1>
      <Form method="GET">
        <Grid container spacing={2}>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <TextField label="Player Name" name="player_name" fullWidth />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <TextField label="Player ID" name="player_id" fullWidth />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <Autocomplete
              options={countryOptions}
              getOptionLabel={(option) => option.name}
              value={
                countryOptions.find((c) => c.code === selectedCountry) || null
              }
              onChange={(event, newValue) => {
                setSelectedCountry(newValue?.code || "");
              }}
              renderOption={({ key, ...props }, option) => (
                <li key={key} {...props}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <CountryFlag country={option.code} />
                    <span>{option.name}</span>
                  </Stack>
                </li>
              )}
              renderInput={({ key, ...params }) => (
                <>
                  <TextField key={key} {...params} label="Country" fullWidth />
                  {/* A hacky way to submit the country code but display the country name */}
                  <input
                    type="hidden"
                    name="country"
                    value={selectedCountry ?? ""}
                  />
                </>
              )}
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <Stack
              sx={{
                width: "100%",
                border: (theme) => `1px solid ${theme.palette.divider}`,
                borderRadius: "4px",
                p: 1,
              }}
              direction="row"
              spacing={1}
              alignItems="center"
              justifyContent="space-between"
            >
              <Stack
                direction="row"
                spacing={1}
                alignItems="center"
                flexWrap="wrap"
              >
                {selectedEmoji.map((emoji) => (
                  <Chip
                    key={emoji.id}
                    size={"medium"}
                    label={<Emoji emoji={emoji} size={18} />}
                    onDelete={() =>
                      setSelectedEmoji(
                        selectedEmoji.filter((e) => e.id !== emoji.id)
                      )
                    }
                  />
                ))}
                {selectedEmoji.length === 0 && (
                  <Typography sx={{ pl: 1 }} variant="body" color="text.secondary">
                    Filter by flags
                  </Typography>
                )}
              </Stack>
              <IconButton onClick={handleEmojiButtonClick}>
                <AddReactionIcon />
              </IconButton>
            </Stack>
            <Popover
              open={open}
              anchorEl={anchorEl}
              onClose={handleClose}
              anchorOrigin={{
                vertical: "bottom",
                horizontal: "left",
              }}
            >
              <Suspense
                fallback={
                  <Skeleton variant="rectangular" height={400} width={300} />
                }
              >
                <EmojiPicker
                  set="twitter"
                  data={emojiData}
                  onEmojiSelect={(emoji) => {
                    // Don't allow duplicates
                    if (selectedEmoji.some((e) => e.id === emoji.id)) return;
                    setSelectedEmoji([...selectedEmoji, emoji]);
                  }}
                />
              </Suspense>
            </Popover>
            <input type="hidden" name="flags" value={selectedEmoji.map((e) => e.native).join(",")} />
          </Grid>

          <Grid size={{ xs: 6, md: 3, lg: 2 }}>
            <FormControlLabel
              control={<Switch name="blacklisted" />}
              label="Blacklisted only"
            />
          </Grid>

          <Grid size={{ xs: 6, md: 3, lg: 2 }}>
            <FormControlLabel
              control={<Switch name="exact_name_match" />}
              label="Exact name match"
            />
          </Grid>

          <Grid size={{ xs: 6, md: 3, lg: 2 }}>
            <FormControlLabel
              control={<Switch name="ignore_accent" defaultChecked />}
              label="Ignore accent"
            />
          </Grid>

          <Grid size={{ xs: 6, md: 3, lg: 2 }}>
            <FormControlLabel
              control={<Switch name="is_watched" />}
              label="Watched only"
            />
          </Grid>
        </Grid>

        <Button
          type="submit"
          variant="contained"
          color="primary"
          sx={{ mt: 2 }}
        >
          Search
        </Button>
      </Form>

      <Divider sx={{ my: 2 }} />

      <section>
        <Grid container spacing={1}>
          {players.map((player) => (
            <Grid key={player.player_id} size={{ xs: 12, sm: 6, md: 4, xl: 3 }}>
              <PlayerCard player={player} />
            </Grid>
          ))}
        </Grid>
      </section>
    </div>
  );
}
