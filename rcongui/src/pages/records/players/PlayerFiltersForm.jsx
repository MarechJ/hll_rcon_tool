import {
  Button,
  TextField,
  FormControlLabel,
  Switch,
  Stack,
  Chip,
  Popover,
  IconButton,
  Skeleton,
  Typography,
} from "@mui/material";
import { Form, useNavigation, useSubmit } from "react-router-dom";
import { Autocomplete } from "@mui/material";
import { CountryFlag } from "@/components/shared/CountryFlag";
import { useState, Suspense, lazy } from "react";
import countries from "country-list";
import emojiData from "@emoji-mart/data/sets/15/twitter.json";
import Emoji from "@/components/shared/Emoji";
import AddReactionIcon from "@mui/icons-material/AddReaction";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import dayjs from "dayjs";

const EmojiPicker = lazy(() => import("@emoji-mart/react"));

// Get all countries for autocomplete
const countryOptions = countries.getCodes().map((code) => ({
  code: code.toLowerCase(),
  name: countries.getName(code),
}));

export default function PlayerFiltersForm({ fields }) {
  const submit = useSubmit();
  const navigation = useNavigation();
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
      ignore_accent: false,
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
            ampm={false}
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
            ampm={false}
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
  );
}

