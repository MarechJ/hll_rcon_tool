import { cmd } from "@/utils/fetchUtils";
import {
  Button,
  TextField,
  FormControlLabel,
  Switch,
  Stack,
  Grid2 as Grid,
  Chip,
  Popover,
  IconButton,
  Skeleton,
  Typography,
  LinearProgress,
} from "@mui/material";
import {
  Form,
  useLoaderData,
  useNavigation,
  useSubmit,
} from "react-router-dom";
import { Autocomplete } from "@mui/material";
import { CountryFlag } from "@/components/shared/CountryFlag";
import { useMemo, useState, Suspense, lazy, memo } from "react";
import countries from "country-list";
import PlayerCard from "@/components/shared/card/PlayerCard";
import { useGlobalStore } from "@/hooks/useGlobalState";
import emojiData from "@emoji-mart/data/sets/15/twitter.json";
import Emoji from "@/components/shared/Emoji";
import AddReactionIcon from "@mui/icons-material/AddReaction";

import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import dayjs from "dayjs";
import NavPagination from "@/pages/stats/games/nav-pagination";
import { Box } from "@mui/system";

const EmojiPicker = lazy(() => import("@emoji-mart/react"));

// Get all countries for autocomplete
const countryOptions = countries.getCodes().map((code) => ({
  code: code.toLowerCase(),
  name: countries.getName(code),
}));

// Create a memoized version of PlayerCard
const MemoizedPlayerCard = memo(PlayerCard);

// Create a separate component for the players section
const PlayersGrid = memo(({ players, ...props }) => {
  return (
    <Grid container spacing={1} {...props}>
      {players.map((player) => (
        <Grid
          key={player.player_id}
          size={{ xs: 12, sm: 6, md: 4, lg: "auto" }}
        >
          <MemoizedPlayerCard player={player} />
        </Grid>
      ))}
    </Grid>
  );
});

export const loader = async ({ request }) => {
  const url = new URL(request.url);

  const player_name = url.searchParams.get("player_name") ?? "";
  const player_id = url.searchParams.get("player_id") ?? "";

  const last_seen_from = url.searchParams.get("last_seen_from") ?? "";
  const last_seen_till = url.searchParams.get("last_seen_till") ?? "";

  const page = url.searchParams.get("page")
    ? Number(url.searchParams.get("page"))
    : 1;
  const page_size = url.searchParams.get("page_size")
    ? Number(url.searchParams.get("page_size"))
    : 50;

  const flags = url.searchParams.get("flags")
    ? url.searchParams.get("flags").split(",")
    : [];
  const country = url.searchParams.get("country") ?? "";

  const blacklisted = url.searchParams.get("blacklisted") ?? false;
  const exact_name_match = url.searchParams.get("exact_name_match") ?? false;
  const ignore_accent = url.searchParams.get("ignore_accent") ?? true;
  const is_watched = url.searchParams.get("is_watched") ?? false;

  const fields = {
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
    last_seen_from,
    last_seen_till,
  };

  // In the background, this command is POST request therefore the payload and not params
  const playersRecords = await cmd.GET_PLAYERS_RECORDS({
    payload: Object.fromEntries(
      Object.entries(fields).filter(
        ([_, value]) => value !== "" && value !== null
      )
    ),
  });

  const bans = await cmd.GET_BANS();

  return {
    players: playersRecords.result.players.map((player) => ({
      ...player,
      is_banned: bans.some((ban) => ban.player_id === player.player_id),
    })),
    total_pages:
      page_size > 0
        ? Math.ceil(Number(playersRecords.result.total) / page_size)
        : 1,
    page: Number(page),
    fields,
  };
};

export default function PlayersRecords() {
  const { players: playersData, fields, total_pages, page } = useLoaderData();
  const submit = useSubmit();
  const navigation = useNavigation();
  const server = useGlobalStore((state) => state.serverState);
  const [formFields, setFormFields] = useState({
    player_name: fields.player_name || "",
    player_id: fields.player_id || "",
    blacklisted: !!fields.blacklisted,
    exact_name_match: !!fields.exact_name_match,
    ignore_accent: !!fields.ignore_accent,
    is_watched: !!fields.is_watched,
    last_seen_from: fields.last_seen_from ? dayjs(fields.last_seen_from) : null,
    last_seen_till: fields.last_seen_till ? dayjs(fields.last_seen_till) : null,
  });
  const [selectedCountry, setSelectedCountry] = useState(fields.country);
  const [selectedEmoji, setSelectedEmoji] = useState(fields.flags);
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

  const handleReset = () => {
    setFormFields({
      player_name: "",
      player_id: "",
      blacklisted: false,
      exact_name_match: false,
      ignore_accent: true,
      is_watched: false,
      last_seen_from: null,
      last_seen_till: null,
    });
    setSelectedCountry("");
    setSelectedEmoji([]);
    submit(null, { method: "GET" });
  };

  const handleInputChange = (e) => {
    const { name, value, checked } = e.target;
    setFormFields((prev) => ({
      ...prev,
      [name]: e.target.type === "checkbox" ? checked : value,
    }));
  };

  return (
    <div>
      <Stack direction={{ xs: "column", lg: "row" }} spacing={1} sx={{ mt: 2 }}>
        <Form method="GET">
          <Stack spacing={2} sx={{ width: { xs: "100%", lg: "300px" } }}>
            <TextField
              value={formFields.player_name}
              onChange={handleInputChange}
              label="Player Name"
              name="player_name"
              fullWidth
            />

            <TextField
              value={formFields.player_id}
              onChange={handleInputChange}
              label="Player ID"
              name="player_id"
              fullWidth
            />

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
                  <Typography
                    sx={{ pl: 1 }}
                    variant="body"
                    color="text.secondary"
                  >
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
            <input
              type="hidden"
              name="flags"
              value={selectedEmoji.map((e) => e.native).join(",")}
            />

            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DateTimePicker
                value={formFields.last_seen_from}
                onChange={(newValue) =>
                  setFormFields((prev) => ({
                    ...prev,
                    last_seen_from: newValue,
                  }))
                }
                label="Last seen from"
                name="last_seen_from"
                format="MMMM DD, YYYY HH:mm"
                timezone="UTC"
                slotProps={{
                  textField: { fullWidth: true },
                }}
              />
            </LocalizationProvider>

            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DateTimePicker
                value={formFields.last_seen_till}
                onChange={(newValue) =>
                  setFormFields((prev) => ({
                    ...prev,
                    last_seen_till: newValue,
                  }))
                }
                label="Last seen till"
                name="last_seen_till"
                format="MMMM DD, YYYY HH:mm"
                timezone="UTC"
                slotProps={{
                  textField: { fullWidth: true },
                }}
              />
            </LocalizationProvider>

            <FormControlLabel
              control={
                <Switch
                  name="blacklisted"
                  checked={formFields.blacklisted}
                  onChange={handleInputChange}
                />
              }
              label="Blacklisted only"
            />

            <FormControlLabel
              control={
                <Switch
                  name="exact_name_match"
                  checked={formFields.exact_name_match}
                  onChange={handleInputChange}
                />
              }
              label="Exact name match"
            />

            <FormControlLabel
              control={
                <Switch
                  name="ignore_accent"
                  checked={formFields.ignore_accent}
                  onChange={handleInputChange}
                />
              }
              label="Ignore accent"
            />

            <FormControlLabel
              control={
                <Switch
                  name="is_watched"
                  checked={formFields.is_watched}
                  onChange={handleInputChange}
                />
              }
              label="Watched only"
            />
          </Stack>

          <Stack direction="column" spacing={1} sx={{ mt: 2 }}>
            <Button
              variant="contained"
              color="secondary"
              sx={{ mt: 2 }}
              onClick={handleReset}
              disabled={navigation.state === "loading"}
            >
              Reset
            </Button>

            <Button
              type="submit"
              variant="contained"
              color="primary"
              sx={{ mt: 2 }}
              disabled={navigation.state === "loading"}
            >
              Search
            </Button>
          </Stack>
        </Form>

        <Stack component="section" id="players-section" spacing={1} sx={{ width: "100%" }}>
          <Box sx={{ height: 4 }}>
            {navigation.state === "loading" && <LinearProgress sx={{ height: 4 }} />}
          </Box>
          <NavPagination
            page={page}
            maxPages={total_pages}
            disabled={navigation.state === "loading"}
          />
          <PlayersGrid players={players} />
          <Box sx={{ flexGrow: 1 }} />
          <NavPagination
            page={page}
            maxPages={total_pages}
            disabled={navigation.state === "loading"}
          />
        </Stack>
      </Stack>
    </div>
  );
}
