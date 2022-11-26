import React from "react";
import {
  Grid,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@material-ui/core";
import DeleteIcon from "@material-ui/icons/Delete";
import AddIcon from "@material-ui/icons/Add";

const AdminRole = ({ classes, role, setRole, roles }) => (
  <FormControl className={classes.formControl}>
    <InputLabel shrink>Role</InputLabel>
    <Select value={role} onChange={(e) => setRole(e.target.value)} displayEmpty>
      {roles.map((r) => (
        <MenuItem value={r}>{r}</MenuItem>
      ))}
    </Select>
  </FormControl>
);

const AddAdminItem = ({
  classes,
  name,
  setName,
  steamID64,
  setSteamID64,
  role,
  setRole,
  roles,
  onAdd,
}) => (
  <ListItem>
    <Grid container>
      <Grid item xs={4} className={classes.paddingRight}>
        <TextField
          InputLabelProps={{
            shrink: true,
          }}
          label="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </Grid>
      <Grid item xs={4} className={classes.paddingLeft}>
        <TextField
          InputLabelProps={{
            shrink: true,
          }}
          label="SteamID64"
          value={steamID64}
          onChange={(e) => setSteamID64(e.target.value)}
        />
      </Grid>
      <Grid item xs={4} className={classes.paddingLeft}>
        <AdminRole
          classes={classes}
          role={role}
          setRole={setRole}
          roles={roles}
        />
      </Grid>
    </Grid>
    <ListItemSecondaryAction>
      <IconButton
        edge="end"
        aria-label="delete"
        onClick={() =>
          onAdd(name, steamID64, role).then(() => {
            setName("");
            setSteamID64("");
            setRole("");
          })
        }
      >
        <AddIcon />
      </IconButton>
    </ListItemSecondaryAction>
  </ListItem>
);

const AdminsEditableList = ({
  classes,
  peopleList,
  roles,
  onDelete,
  onAdd,
}) => {
  const [name, setName] = React.useState("");
  const [steamID64, setSteamID64] = React.useState("");
  const [role, setRole] = React.useState("");

  return (
    <React.Fragment>
      <List dense>
        <AddAdminItem
          classes={classes}
          name={name}
          setName={setName}
          steamID64={steamID64}
          setSteamID64={setSteamID64}
          roles={roles}
          role={role}
          setRole={setRole}
          onAdd={onAdd}
        />
        {peopleList.map((obj) => (
          <ListItem key={obj.steam_id_64}>
            <ListItemText
              primary={"[" + obj.role + "] " + obj.name}
              secondary={obj.steam_id_64}
            />
            <ListItemSecondaryAction>
              <IconButton
                edge="end"
                aria-label="delete"
                onClick={() => onDelete(obj.name, obj.steam_id_64, obj.role)}
              >
                <DeleteIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
        <AddAdminItem
          classes={classes}
          name={name}
          setName={setName}
          steamID64={steamID64}
          setSteamID64={setSteamID64}
          roles={roles}
          role={role}
          setRole={setRole}
          onAdd={onAdd}
        />
      </List>
    </React.Fragment>
  );
};

export default AdminsEditableList;
