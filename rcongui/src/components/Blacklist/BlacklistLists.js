import {
  Button,
  Grid,
  IconButton,
  InputLabel,
  LinearProgress,
  Paper,
  Tooltip,
  Typography,
} from "@material-ui/core";
import useStyles from "../useStyles";
import React from "react";
import { get, handle_http_errors, postData, showResponse } from "../../utils/fetchUtils";
import EditIcon from "@material-ui/icons/Edit";
import DeleteIcon from "@material-ui/icons/Delete";
import BlacklistListTile from "./BlacklistListTile";
import BlacklistListCreateDialog, { BlacklistListCreateButton } from "./BlacklistListCreateDialog";
const SYNC_METHODS = {
  kick_only: "Kick Only",
  ban_on_connect: "Ban On Connect",
  ban_immediately: "Ban Immediately",
}
const BlacklistLists = ({ classes: globalClasses }) => {
  const classes = useStyles();

  const [isLoading, setIsLoading] = React.useState(false);
  const [blacklists, setBlacklists] = React.useState([]);
  const [servers, setServers] = React.useState({});
  
  const [editDialogOpen, setEditDialogOpen] = React.useState(false);
  const [editDialogInitialValues, setEditDialogInitialValues] = React.useState();

  function loadServers() {
    return Promise.all([
      get("get_connection_info")
        .then((response) => showResponse(response, "get_connection_info", false))
        .then((data) => {
          if (data.result) {
            servers[data.result.server_number] = data.result.name;
          }
        })
        .catch(handle_http_errors),
      get("get_server_list")
        .then((response) => showResponse(response, "get_server_list", false))
        .then((data) => {
          data.result?.forEach(
            (server) => {
              servers[server.server_number] = server.name;
            }
          );
        })
        .catch(handle_http_errors)
    ]);
  }

  function loadBlacklists() {
    return get("get_blacklists")
      .then((response) => showResponse(response, "get_blacklists", false))
      .then((data) => {
        if (data.result) {
          setBlacklists(data.result);
        }
      })
      .catch(handle_http_errors);
  }

  function onBlacklistCreate(data) {
    postData(`${process.env.REACT_APP_API_URL}create_blacklist`, {
      name: data.name,
      servers: data.servers,
      sync: data.syncMethod,
    })
      .then((response) =>
        showResponse(response, `Blacklist ${data.name} was created`, true)
      )
      .catch(handle_http_errors)
      .then(loadBlacklists);
  }
  
  function onEditBlacklist(blacklist) {
    setEditDialogInitialValues({
      id: blacklist.id,
      name: blacklist.name,
      servers: blacklist.servers,
      syncMethod: blacklist.sync
    })
    setEditDialogOpen(true);
  }

  function onEditDialogSubmit(data) {
    const blacklistId = editDialogInitialValues.id;
    postData(`${process.env.REACT_APP_API_URL}edit_blacklist`, {
      blacklist_id: blacklistId,
      name: data.name,
      servers: data.servers,
      sync_method: data.syncMethod,
    })
      .then((response) =>
        showResponse(response, `Blacklist ${data.name} was edited`, true)
      )
      .catch(handle_http_errors)
      .then(loadBlacklists);
  }

  function onDeleteBlacklist(blacklist) {
    postData(`${process.env.REACT_APP_API_URL}delete_blacklist`, {
      blacklist_id: blacklist.id,
    })
      .then((response) =>
        showResponse(response, `Blacklist ${blacklist.name} was deleted`, true)
      )
      .catch(handle_http_errors)
      .then(loadBlacklists);
  }
  
  React.useEffect(() => {
    setIsLoading(true);
    loadServers()
      .then(loadBlacklists)
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <React.Fragment>
      <Grid container spacing={3} direction="column" justify="center" className={globalClasses.padding}>
        <Grid item>
          {isLoading ? <LinearProgress color="secondary" /> : ""}
        </Grid>
        <Grid item container spacing={5} direction="column" alignItems="center">
          {blacklists.map((blacklist) => (
            <Grid key={blacklist.id} item style={{width: "100%", maxWidth: 1600}}>
              <BlacklistListTile
                classes={globalClasses}
                servers={servers}
                blacklist={blacklist}
                onEdit={onEditBlacklist}
                onDelete={onDeleteBlacklist}
              />
            </Grid>
          ))}
        </Grid>
        <Grid item>
          <Grid container spacing={2} justify="center">
            <Grid item>
              <BlacklistListCreateButton
                servers={servers}
                onSubmit={onBlacklistCreate}
              />
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                color="primary"
                size="large"
                onClick={(e) => {
                  e.preventDefault();
                  window.location.hash = "#/blacklists";
                }}
              >
                Back To Records
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      
      <BlacklistListCreateDialog
        open={editDialogOpen}
        setOpen={setEditDialogOpen}
        servers={servers}
        onSubmit={onEditDialogSubmit}
        initialValues={editDialogInitialValues}
      />
    </React.Fragment>
  )
}

export default BlacklistLists;