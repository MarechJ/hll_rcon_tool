import {
  Button,
  FormControl,
  Grid,
  InputLabel,
  NativeSelect,
  TextField,
  Typography,
} from "@material-ui/core";
import React from "react";
import { fromJS, List, Map } from "immutable";
import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";
import Padlock from "./padlock";

const VoteMapConfig = () => {
  const [config, setConfig] = React.useState(new Map());
  const [status, setStatus] = React.useState(new Map());

  const saveConfig = (kv) => {
    let mapAsObject = {
      ...Object.fromEntries(config.entries()),
      ...kv,
    };
    /* TODO: This is kind of dumb but I don't know a better way to do it */
    delete mapAsObject.size;
    delete mapAsObject._root;
    delete mapAsObject.__altered;
    return postData(
      `${process.env.REACT_APP_API_URL}set_votemap_config`,
      mapAsObject
    )
      .then((res) => showResponse(res, "set_votemap_config", true))
      .then(loadData)
      .catch(handle_http_errors);
  };

  const loadData = () => {
    get("get_votemap_status")
      .then((res) => showResponse(res, "get_votemap_status", false))
      .then((data) => (data.failed ? "" : setStatus(fromJS(data.result))))
      .catch(handle_http_errors);
    get("get_votemap_config")
      .then((res) => showResponse(res, "get_votemap_config", false))
      .then((data) => (data.failed ? "" : setConfig(fromJS(data.result))))
      .catch(handle_http_errors);
  };

  const resetVotes = () =>
    postData(`${process.env.REACT_APP_API_URL}reset_votemap_state`)
      .then((res) => showResponse(res, "reset_votemap_state", true))
      .then((res) => (res.failed ? "" : setStatus(fromJS(res.result))))
      .catch(handle_http_errors);

  React.useEffect(() => {
    loadData();
    const handle = setInterval(loadData, 60000);
    return () => clearInterval(handle);
  }, []);

  return (
    <Grid
      container
      spacing={2}
      justify="flex-start"
      alignContent="center"
      alignItems="center"
    >
      <Grid item xs={12}>
        <Padlock
          label="Next Map Vote Enabled"
          checked={config.get("enabled", false)}
          handleChange={(v) => saveConfig({ enabled: v })}
        />
      </Grid>
      <Grid container spacing={1} alignItems="center">
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={2}
            rowsMax={4}
            label="Reminder text sent to player to vote:"
            helperText="Make sure you add {map_selection} in your text"
            value={config.get("instruction_text", "")}
            onChange={(e) =>
              setConfig(config.set("instruction_text", e.target.value))
            }
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={2}
            rowsMax={4}
            label="Thank you for voting message:"
            helperText="The reply to player after they voted. You can use {player_name} and {map_name} in the text. Leave blank if you don't want the confirmation message"
            value={config.get("thank_you_text", "")}
            onChange={(e) =>
              setConfig(config.set("thank_you_text", e.target.value))
            }
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={2}
            rowsMax={4}
            label="Help text:"
            helperText="This text will show to the player in case of a bad !votemap command, or if the user types !votemap help"
            value={config.get("help_text", "")}
            onChange={(e) => setConfig(config.set("help_text", e.target.value))}
          />
        </Grid>
        <Grid item xs={12}>
          <Button variant="outlined" onClick={() => saveConfig(config)}>
            Save texts
          </Button>
        </Grid>
      </Grid>
      <Grid item>
        <TextField
          type="number"
          inputProps={{ min: 0, max: 90 }}
          label="Reminder frequency minutes:"
          helperText="Will remind players who haven't vote with a PM. Set to 0 to disable (will only show once on map end)."
          value={config.get("reminder_frequency_minutes", false)}
          onChange={(e) =>
            saveConfig({ reminder_frequency_minutes: e.target.value })
          }
        />
      </Grid>
      <Grid item>
        <Padlock
          label="Allow user to opt-out of vote map reminders by typing !votemap never"
          checked={config.get("allow_opt_out", false)}
          handleChange={(v) => saveConfig({ allow_opt_out: v })}
        />
      </Grid>
      <Grid item>
        <TextField
          type="number"
          inputProps={{ min: 2, max: 10 }}
          label="Number of options in selection:"
          helperText="The amount of maps that should be offered in the vote"
          value={config.get("number_of_options", false)}
          onChange={(e) => saveConfig({ number_of_options: e.target.value })}
        />
      </Grid>
      <Grid item>
        <TextField
          type="number"
          inputProps={{ min: 0, max: 1, step: 0.05 }}
          label="Ratio of offensives:"
          helperText="The ratio of offensive maps in the selection"
          value={config.get("ratio_of_offensives", false)}
          onChange={(e) => saveConfig({ ratio_of_offensives: e.target.value })}
        />
      </Grid>
      <Grid item>
        {" "}
        <TextField
          type="number"
          inputProps={{ min: 0, max: 6, step: 1 }}
          label="Number of recently played maps excluded:"
          helperText="Exclude the last N played maps from the selection. The current map is always excluded."
          value={config.get("number_last_played_to_exclude", false)}
          onChange={(e) =>
            saveConfig({
              number_last_played_to_exclude: e.target.value,
            })
          }
        />
      </Grid>
      <Grid item>
        <Padlock
          label="Consider offensive map being the same as warfare when excluding:"
          checked={config.get("consider_offensive_same_map", false)}
          handleChange={(v) => saveConfig({ consider_offensive_same_map: v })}
        />
      </Grid>

      <Grid item>
        <Padlock
          label="Allow consecutive offensive map"
          checked={config.get("allow_consecutive_offensives", false)}
          handleChange={(v) => saveConfig({ allow_consecutive_offensives: v })}
        />
      </Grid>

      <Grid item>
        <Padlock
          label="Allow consecutive offensive where a team would play defense twice in a row. E.g off_ger followed by off_us"
          checked={config.get(
            "allow_consecutive_offensives_opposite_sides",
            false
          )}
          handleChange={(v) =>
            saveConfig({
              allow_consecutive_offensives_opposite_sides: v,
            })
          }
        />
      </Grid>

      <Grid item>
        <FormControl>
          <InputLabel>Default map method (when no votes)</InputLabel>
          <NativeSelect
            value={config.get("default_method", "")}
            onChange={(e) => saveConfig({ default_method: e.target.value })}
          >
            <option value="least_played_from_suggestions">
              Pick least played map from suggestions
            </option>
            <option value="least_played_from_all_map">
              Pick least played map from all maps
            </option>
            <option value="random_from_suggestions">
              Pick randomly from suggestions
            </option>
            <option value="random_from_all_maps">
              Pick randomly from all maps
            </option>
          </NativeSelect>
        </FormControl>
      </Grid>
      <Grid item>
        <Padlock
          label="Allow default map to be an offensive"
          checked={config.get("allow_default_to_offensive", false)}
          handleChange={(v) => saveConfig({ allow_default_to_offensive: v })}
        />
      </Grid>
      <Grid item xs={12}>
        <Grid
          container
          justify="flex-start"
          alignContent="stretch"
          alignItems="stretch"
          orientation="column"
        >
          <Grid item xs={12}>
            <Typography variant="h6">Current vote status</Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="body1">Votes:</Typography>
            <pre>
              {status
                .get("votes", new Map())
                .entrySeq()
                .map((o) => `${o[0]}: ${o[1]}\n`)}
            </pre>
          </Grid>
          <Grid item xs={6} sm={4}>
            <Typography variant="body1">Map selection:</Typography>
            <pre>
              {status.get("selection", new List()).map((v) => `${v}\n`)}
            </pre>
          </Grid>
          <Grid item xs={6} sm={4}>
            <Typography variant="body1">Results:</Typography>
            <pre>
              {status
                .get("results", new Map())
                .get("winning_maps", new List())
                .map((o) => `${o.get(0)}: ${o.get(1)} vote(s)\n`)}
            </pre>
          </Grid>
          <Grid xs={12}>
            <Button
              variant="outlined"
              color="secondary"
              onClick={() => {
                if (window.confirm("Are you sure?") === true) {
                  resetVotes().then(loadData);
                }
              }}
            >
              RESET SELECTION & VOTES
            </Button>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
};

export default VoteMapConfig;
