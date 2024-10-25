import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  LinearProgress,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import React from "react";
import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "@/utils/fetchUtils";
import BlacklistListTile from "@/components/Blacklist/BlacklistListTile";
import BlacklistListCreateDialog, {
  BlacklistListCreateButton,
} from "@/components/Blacklist/BlacklistListCreateDialog";
import { Link } from "react-router-dom";

const BlacklistLists = () => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [blacklists, setBlacklists] = React.useState([]);
  const [servers, setServers] = React.useState({});
  const [selectedBlacklist, setSelectedBlacklist] = React.useState(null);
  const [editDialogOpen, setEditDialogOpen] = React.useState(false);
  const [editDialogInitialValues, setEditDialogInitialValues] =
    React.useState();

  function handleCloseDeleteDialog() {
    setSelectedBlacklist(null);
  }

  function handleDeleteClick(blacklist) {
    setSelectedBlacklist(blacklist);
  }

  function handleBlacklistDelete() {
    deleteBlacklist(selectedBlacklist);
    handleCloseDeleteDialog();
  }

  function loadServers() {
    return Promise.all([
      get("get_connection_info")
        .then((response) =>
          showResponse(response, "get_connection_info", false)
        )
        .then((data) => {
          if (data.result) {
            setServers((prevState) => ({
              ...prevState,
              [data.result.server_number]: data.result.name,
            }));
          }
        })
        .catch(handle_http_errors),
      get("get_server_list")
        .then((response) => showResponse(response, "get_server_list", false))
        .then((data) => {
          if (data?.result) {
            setServers((prevState) => ({
              ...prevState,
              ...data.result.reduce((acc, server) => {
                acc[server.server_number] = server.name;
                return acc;
              }, {}),
            }));
          }
        })
        .catch(handle_http_errors),
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
      syncMethod: blacklist.sync,
    });
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

  function deleteBlacklist(blacklist) {
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
      <Grid container spacing={3} direction="column" justifyContent="center">
        <Grid>
          {isLoading ? <LinearProgress color="secondary" /> : ""}
        </Grid>
        <Grid container spacing={5} direction="column" alignItems="center">
          {blacklists.map((blacklist) => (
            <Grid
              key={blacklist.id}
              style={{ width: "100%", maxWidth: 1600 }}
            >
              <BlacklistListTile
                servers={servers}
                blacklist={blacklist}
                onEdit={onEditBlacklist}
                onDelete={handleDeleteClick}
              />
            </Grid>
          ))}
        </Grid>
        <Grid>
          <Grid container spacing={2} justifyContent="center">
            <Grid>
              <BlacklistListCreateButton
                servers={servers}
                onSubmit={onBlacklistCreate}
              />
            </Grid>
            <Grid>
              <Button
                component={Link}
                to="/records/blacklists"
                variant="contained"
                color="primary"
                size="large"
              >
                Back To Records
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      {/* CREATE DIALOG */}
      <BlacklistListCreateDialog
        open={editDialogOpen}
        setOpen={setEditDialogOpen}
        servers={servers}
        onSubmit={onEditDialogSubmit}
        initialValues={editDialogInitialValues}
      />
      {/* DELETE DIALOG */}
      <Dialog
        open={selectedBlacklist !== null}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {selectedBlacklist
            ? `Delete blacklist "${selectedBlacklist?.name}"?`
            : "Loading..."}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you certain you want to permanently delete the blacklist and all
            associated records?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleBlacklistDelete} color="secondary" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
};

export default BlacklistLists;
