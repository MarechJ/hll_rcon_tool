import React from "react";
import {
  IconButton,
  List,
  ListItem,
  ListItemSecondaryAction,
  ListItemText,
  TextField,
  Button,
  Tooltip,
  Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import { ForwardCheckBox } from "../commonComponent";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import Grid from "@mui/material/Unstable_Grid2";

import moment from "moment";
import { VipExpirationDialog } from "../VipDialog";
import { fromJS } from "immutable";
import { vipListFromServer } from "../VipDialog/vipFromServer";

const AddVipItem = ({
  name,
  setName,
  playerId,
  setPlayerId,
  onAdd,
}) => (
  <ListItem>
    <Grid container>
      <Grid xs={6} >
        <TextField
          InputLabelProps={{
            shrink: true,
          }}
          label="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </Grid>
      <Grid xs={6} >
        <TextField
          InputLabelProps={{
            shrink: true,
          }}
          label="Player ID"
          value={playerId}
          onChange={(e) => setPlayerId(e.target.value)}
        />
      </Grid>
    </Grid>
    <ListItemSecondaryAction>
      <IconButton
        edge="end"
        aria-label="delete"
        onClick={() => onAdd(name, playerId)}
        size="large">
        <AddIcon />
      </IconButton>
    </ListItemSecondaryAction>
  </ListItem>
);

function setIntervalLimited(callback, interval, x) {
  for (var i = 0; i < x; i++) {
    setTimeout(callback, i * interval);
  }
}

const VipUpload = () => {
  const [selectedFile, setSelectedFile] = React.useState();
  const [isFilePicked, setIsFilePicked] = React.useState(false);
  const [result, setResult] = React.useState(null);

  const changeHandler = (event) => {
    setSelectedFile(event.target.files[0]);
    setIsFilePicked(true);
  };

  const handleSubmission = () => {
    const formData = new FormData();
    formData.append("File", selectedFile);

    fetch(`${process.env.REACT_APP_API_URL}upload_vips`, {
      method: "POST",
      body: formData,
      mode: "cors", // no-cors, *cors, same-origin
      cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
      credentials: "include", // include, *same-origin, omit
    })
      .then((res) => showResponse(res, "upload_vips", true))
      .then((res) => (!res.failed ? pollResult() : ""))
      .catch(handle_http_errors);
    setIsFilePicked(false);
  };

  const getResult = () =>
    get("upload_vips_result")
      .then((res) => showResponse(res, "upload_vips_result", false))
      .then((res) => {
        setResult(JSON.stringify(res.result, null, 2));
        console.log(res);
      });
  const pollResult = () =>
    getResult() && setIntervalLimited(getResult, 2000, 500);

  return (
    <Grid container spacing={1}>
      <Grid xs={6}>
        <Button
          fullWidth
          type="link"
          variant="outlined"
          href={`${process.env.REACT_APP_API_URL}download_vips`}
          target="_blank"
        >
          Download VIPs
        </Button>
      </Grid>
      <Grid xs={6}>
        {isFilePicked ? (
          <Button
            fullWidth
            variant="contained"
            color="primary"
            onClick={handleSubmission}
          >
            submit
          </Button>
        ) : (
          <Tooltip
            title={`Caution this does a total override, deletes all vip then re-add from file.
            The format is a simple text file (same as the downloaded one), one person per line with the player ID first then the name.
            eg: 76561198107873800 Thats my name.
            
            This is not forwarded to your other servers (if you have them)`}
          >
            <Button fullWidth variant="outlined" component="label">
              Upload VIPs
              <input type="file" hidden onChange={changeHandler} />
            </Button>
          </Tooltip>
        )}
      </Grid>

      {result ? (
        <Grid xs={12}>
          <Typography variant="body2" color="secondary">
            The job may take a while, here's the current status, do not resubmit
            unless you see a "finished" or "failed" status:{" "}
          </Typography>
          <pre>{result}</pre>
        </Grid>
      ) : (
        ""
      )}
    </Grid>
  );
};

function nameOf(playerObj) {
  const names = playerObj.get("names");
  if (names.size === 0) {
    return "";
  }
  return playerObj.get("names").get(0).get("name");
}

const VipEditableList = ({
  peopleList,
  onDelete,
  onAdd,
  forward,
  onFowardChange,
}) => {
  const [name, setName] = React.useState("");
  const [player_id, setPlayerId] = React.useState("");
  const [VIPPlayer, setVIPPlayer] = React.useState(false);

  const formatExpirationDate = (player) => {
    if (player.vip_expiration) {
      let date = moment(player.vip_expiration);
      /* For display purposes, show dates really far in the future as indefinite */
      if (date.isSameOrAfter(moment().add(100, "years"))) {
        return "Never";
      } else {
        return moment(player.vip_expiration).format("YYYY-MM-DD HH:mm:ssZ");
      }
    } else {
      return "Never";
    }
  };

  function onOpenAddVipDialog(name, player_id) {
    return setVIPPlayer(
      fromJS({
        names: [
          {
            name: name,
          },
        ],
        player_id: player_id,
      })
    );
  }

  return (
    (<React.Fragment>
      <List dense>
        <ForwardCheckBox bool={forward} onChange={onFowardChange} />
        <AddVipItem
          
          name={name}
          setName={setName}
          playerId={player_id}
          setPlayerId={setPlayerId}
          onAdd={onOpenAddVipDialog}
        />
        {peopleList.map((obj) => (
          <ListItem key={obj.player_id}>
            <ListItemText
              primary={obj.name}
              secondary={obj.player_id + " " + formatExpirationDate(obj)}
            />
            <ListItemSecondaryAction>
              <IconButton
                edge="end"
                aria-label="delete"
                onClick={() => onDelete(obj.name, obj.player_id)}
                size="large">
                <DeleteIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
        <AddVipItem
          
          name={name}
          setName={setName}
          playerId={player_id}
          setPlayerId={setPlayerId}
          onAdd={onOpenAddVipDialog}
        />
        <ForwardCheckBox bool={forward} onChange={onFowardChange} />
        <VipExpirationDialog
          open={VIPPlayer}
          player={VIPPlayer}
          vips={vipListFromServer(peopleList)}
          onDeleteVip={(playerObj) =>
            onDelete(nameOf(playerObj), playerObj.get("player_id"))
          }
          handleClose={() => setVIPPlayer(false)}
          handleConfirm={(playerObj, expirationTimestamp) => {
            console.log(`vips.js expirationTimestamp=${expirationTimestamp}`);
            onAdd(
              nameOf(playerObj),
              playerObj.get("player_id"),
              expirationTimestamp
            );
            setVIPPlayer(false);
          }}
        />
      </List>
    </React.Fragment>)
  );
};

export default VipEditableList;
export { VipUpload };
