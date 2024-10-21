import React from "react";
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  FormControl,
  FormControlLabel,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Switch,
  TextField,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { DesktopDateTimePicker } from '@mui/x-date-pickers/DesktopDateTimePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import data from '@emoji-mart/data'
import EmojiPicker from "@emoji-mart/react";
import Grid from "@mui/material/Grid2";

const SearchBar = ({
  name,
  playerId,
  lastSeenFrom,
  lastSeenUntil,
  blacklistedOnly,
  pageSize,
  setPageSize,
  setName,
  setPlayerId,
  setLastSeenFrom,
  setLastSeenUntil,
  setBlacklistedOnly,
  isWatchedOnly,
  setIsWatchedOnly,
  onSearch,
  ignoreAccent,
  setIgnoreAccent,
  exactMatch,
  setExactMatch,
  flags,
  setFlags,
  country,
  setCountry,
}) => {
  const [showEmojiPicker, setShowEmojiPicker] = React.useState(false);
  //const toggleEmojis = () => setShowEmojiPicker(!showEmojiPicker)

  return (
    (<form>
      <Grid
        container
        spacing={1}
        alignContent="center"
        alignItems="center"
        justifyContent="space-evenly"
      >
        <Grid>
          <TextField
            label="Search by Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </Grid>
        <Grid>
          <FormControlLabel
            control={
              <Switch
                checked={ignoreAccent}
                onChange={(e) => setIgnoreAccent(e.target.checked)}
                color="primary"
              />
            }
            label="Ignore Accents"
            labelPlacement="top"
          />
        </Grid>
        <Grid>
          <FormControlLabel
            control={
              <Switch
                checked={exactMatch}
                onChange={(e) => setExactMatch(e.target.checked)}
                color="primary"
              />
            }
            label="Exact match"
            labelPlacement="top"
          />
        </Grid>
        <Grid>
          <TextField
            label="Search by Player ID"
            value={playerId}
            onChange={(e) => setPlayerId(e.target.value)}
          />
        </Grid>
        <Grid>
          <TextField
            label="Flag"
            value={flags}
            onChange={(e) => setFlags(e.target.value)}
            onFocus={() => setShowEmojiPicker(true)}
          />
          {showEmojiPicker ? (
            <Card>
              <CardHeader
                title="Pick emojis"
                action={
                  <IconButton onClick={() => setShowEmojiPicker(false)} size="large">
                    <CloseIcon />
                  </IconButton>
                }
              />
              <CardContent>
              <EmojiPicker
                style={{ border: '1px solid red' }}
                dynamicWidth={true}
                perLine={8}
                data={data}
                onEmojiSelect={(emoji) =>
                  setFlags(flags + emoji.native + ",")
                }
              />
              </CardContent>
            </Card>
          ) : (
            ""
          )}
        </Grid>

        <Grid>
          <TextField
            label="Steam country (iso)"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          />
        </Grid>
        <Grid>
          {/* <MuiPickersUtilsProvider utils={MomentUtils}>
            <DateTimePicker
              label="Last seen from"
              value={lastSeenFrom}
              onChange={setLastSeenFrom}
              format="YYYY/MM/DD HH:mm"
            />
          </MuiPickersUtilsProvider> */}
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DesktopDateTimePicker
              label="Last seen from"
              onChange={(value) => console.log(value)} // send value to hook form
              format='LLL'
            />
          </LocalizationProvider>
        </Grid>
        <Grid>
          {/* <MuiPickersUtilsProvider utils={MomentUtils}>
            <DateTimePicker
              label="Last seen until"
              value={lastSeenUntil}
              onChange={setLastSeenUntil}
              format="YYYY/MM/DD HH:mm"
            />
          </MuiPickersUtilsProvider> */}
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DesktopDateTimePicker
              label="Last seen until"
              onChange={(value) => console.log(value)} // send value to hook form
              format='LLL'
            />
          </LocalizationProvider>
        </Grid>
        <Grid>
          <FormControlLabel
            control={
              <Switch
                checked={blacklistedOnly}
                onChange={(e) => setBlacklistedOnly(e.target.checked)}
                color="primary"
              />
            }
            label="Blacklisted only"
            labelPlacement="top"
          />
        </Grid>
        <Grid>
          <FormControlLabel
            control={
              <Switch
                checked={isWatchedOnly}
                onChange={(e) => setIsWatchedOnly(e.target.checked)}
                color="primary"
              />
            }
            label="Watched only"
            labelPlacement="top"
          />
        </Grid>
        <Grid
          size={{
            xs: 4,
            xl: 1
          }}>
          <FormControl fullWidth>
            <InputLabel>Page size</InputLabel>
            <Select
              value={pageSize}
              onChange={(e) => setPageSize(e.target.value)}
            >
              <MenuItem value={10}>10</MenuItem>
              <MenuItem value={20}>20</MenuItem>
              <MenuItem value={30}>30</MenuItem>
              <MenuItem value={40}>40</MenuItem>
              <MenuItem value={50}>50</MenuItem>
              <MenuItem value={100}>100</MenuItem>
              <MenuItem value={200}>200</MenuItem>
              <MenuItem value={500}>500</MenuItem>
              <MenuItem value={1000}>1000</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            onClick={(e) => {
              e.preventDefault();
              onSearch();
            }}
          >
            Load results
          </Button>
        </Grid>
      </Grid>
    </form>)
  );
};

export default SearchBar;
