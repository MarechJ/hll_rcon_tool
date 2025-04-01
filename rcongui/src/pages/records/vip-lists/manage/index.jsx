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
import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "@/utils/fetchUtils";
import VipListListTile from "@/components/VipList/VipListListTile";
import VipListCreateDialog, {
  VipListListCreateButton,
} from "@/components/VipList/VipListListCreateDialog";
import { Link } from "react-router-dom";
import { Fragment, useEffect, useState } from "react";

const VipListLists = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [vipLists, setVipLists] = useState([]);
  const [servers, setServers] = useState({});
  const [selectedVipList, setSelectedVipList] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editDialogInitialValues, setEditDialogInitialValues] = useState();

  function handleCloseDeleteDialog() {
    setSelectedVipList(null);
  }

  function handleDeleteClick(vipList) {
    setSelectedVipList(vipList);
  }

  function handleVipListDelete() {
    deleteVipList(selectedVipList);
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

  function loadVipLists() {
    return get("get_vip_lists")
      .then((response) => showResponse(response, "get_vip_lists", false))
      .then((data) => {
        if (data.result) {
          setVipLists(data.result);
        }
      })
      .catch(handle_http_errors);
  }

  function onVipListCreate(data) {
    postData(`${process.env.REACT_APP_API_URL}create_vip_list`, {
      name: data.name,
      servers: data.servers,
      sync: data.syncMethod,
    })
      .then((response) =>
        showResponse(response, `VIP List ${data.name} was created`, true)
      )
      .catch(handle_http_errors)
      .then(loadVipLists);
  }

  function onEditVipList(vipList) {
    setEditDialogInitialValues({
      id: vipList.id,
      name: vipList.name,
      servers: vipList.servers,
      syncMethod: vipList.sync,
    });
    setEditDialogOpen(true);
  }

  function onEditDialogSubmit(data) {
    const vipListId = editDialogInitialValues.id;
    postData(`${process.env.REACT_APP_API_URL}edit_vip_list`, {
      vip_list_id: vipListId,
      name: data.name,
      servers: data.servers,
      sync_method: data.syncMethod,
    })
      .then((response) =>
        showResponse(response, `VIP List ${data.name} was edited`, true)
      )
      .catch(handle_http_errors)
      .then(loadVipLists);
  }

  function deleteVipList(vipList) {
    postData(`${process.env.REACT_APP_API_URL}delete_vip_list`, {
      vip_list_id: vipList.id,
    })
      .then((response) =>
        showResponse(response, `VIP List ${vipList.name} was deleted`, true)
      )
      .catch(handle_http_errors)
      .then(loadVipLists);
  }

  useEffect(() => {
    setIsLoading(true);
    loadServers()
      .then(loadVipLists)
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <Fragment>
      <Grid container spacing={3} direction="column" justifyContent="center">
        <Grid>{isLoading ? <LinearProgress color="secondary" /> : ""}</Grid>
        <Grid container spacing={5} direction="column" alignItems="center">
          {vipLists.map((vipList) => (
            <Grid key={vipList.id} style={{ width: "100%", maxWidth: 1600 }}>
              <VipListListTile
                servers={servers}
                vipList={vipList}
                onEdit={onEditVipList}
                onDelete={handleDeleteClick}
              />
            </Grid>
          ))}
        </Grid>
        <Grid>
          <Grid container spacing={2} justifyContent="center">
            <Grid>
              <VipListListCreateButton
                servers={servers}
                onSubmit={onVipListCreate}
              />
            </Grid>
            <Grid>
              <Button
                component={Link}
                to="/records/vip-lists"
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
      <VipListCreateDialog
        open={editDialogOpen}
        setOpen={setEditDialogOpen}
        servers={servers}
        onSubmit={onEditDialogSubmit}
        initialValues={editDialogInitialValues}
      />
      {/* DELETE DIALOG */}
      <Dialog
        open={selectedVipList !== null}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {selectedVipList
            ? `Delete VIP List "${selectedVipList?.name}"?`
            : "Loading..."}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you certain you want to permanently delete the VIP List and all
            associated records?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleVipListDelete} color="secondary" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Fragment>
  );
};

export default VipListLists;
