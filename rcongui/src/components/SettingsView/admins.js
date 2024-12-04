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
import PlayerAutocomplete from "./playerAutocomplete";

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
  playerId,
  setPlayerId,
  role,
  setRole,
  roles,
  onAdd,
}) => (
  <ListItem>
    <Grid container>
      <Grid item xs={4} className={classes.paddingRight}>
        <PlayerAutocomplete classes={classes} name={name} setName={setName} playerId={playerId} setPlayerId={setPlayerId}/>
      </Grid>
      <Grid item xs={4} className={classes.paddingLeft}>
        <TextField
          InputLabelProps={{
            shrink: true,
          }}
          label="Player ID"
          value={playerId}
          onChange={(e) => setPlayerId(e.target.value)}
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
          onAdd(name, playerId, role).then(() => {
            setName("");
            setPlayerId("");
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
  const [playerId, setPlayerId] = React.useState("");
  const [role, setRole] = React.useState("");

  return (
    <React.Fragment>
      <List dense>
        <AddAdminItem
          classes={classes}
          name={name}
          setName={setName}
          playerId={playerId}
          setPlayerId={setPlayerId}
          roles={roles}
          role={role}
          setRole={setRole}
          onAdd={onAdd}
        />
        {peopleList.map((obj) => (
          <ListItem key={obj.player_id}>
            <ListItemText
              primary={"[" + obj.role + "] " + obj.name}
              secondary={obj.player_id}
            />
            <ListItemSecondaryAction>
              <IconButton
                edge="end"
                aria-label="delete"
                onClick={() => onDelete(obj.name, obj.player_id, obj.role)}
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
          playerId={playerId}
          setPlayerId={setPlayerId}
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
