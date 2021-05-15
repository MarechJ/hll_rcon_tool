import React from "react";
import {Grid, IconButton, List, ListItem, ListItemSecondaryAction, ListItemText, TextField} from "@material-ui/core";
import DeleteIcon from '@material-ui/icons/Delete';
import AddIcon from '@material-ui/icons/Add';
import {ForwardCheckBox} from '../commonComponent'

const AddVipItem = ({ classes, name, setName, steamID64, setSteamID64, onAdd }) => (
    <ListItem>
        <Grid container>
            <Grid item xs={6} className={classes.paddingRight}>
                <TextField InputLabelProps={{
                    shrink: true,
                }} label="Name" value={name} onChange={(e) => setName(e.target.value)} />
            </Grid>
            <Grid item xs={6} className={classes.paddingLeft} >
                <TextField InputLabelProps={{
                    shrink: true,
                }} label="SteamID64" value={steamID64} onChange={(e) => setSteamID64(e.target.value)} />
            </Grid>
        </Grid>
        <ListItemSecondaryAction>
            <IconButton edge="end" aria-label="delete" onClick={() => onAdd(name, steamID64).then(() => { setName(""); setSteamID64("") })}>
                <AddIcon />
            </IconButton>
        </ListItemSecondaryAction>
    </ListItem>
)

const VipEditableList = ({ classes, peopleList, onDelete, onAdd, forward, onFowardChange }) => {
    const [name, setName] = React.useState("")
    const [steamID64, setSteamID64] = React.useState("")

    return <React.Fragment>
        <List dense>
            <ForwardCheckBox bool={forward} onChange={onFowardChange} />
            <AddVipItem classes={classes} name={name} setName={setName} steamID64={steamID64} setSteamID64={setSteamID64} onAdd={onAdd} />
            {peopleList.map(obj => (
                <ListItem key={obj.steam_id_64}>
                    <ListItemText
                        primary={obj.name}
                        secondary={obj.steam_id_64}
                    />
                    <ListItemSecondaryAction>
                        <IconButton edge="end" aria-label="delete" onClick={() => onDelete(obj.name, obj.steam_id_64)}>
                            <DeleteIcon />
                        </IconButton>
                    </ListItemSecondaryAction>
                </ListItem>
            ))}
            <AddVipItem classes={classes} name={name} setName={setName} steamID64={steamID64} setSteamID64={setSteamID64} onAdd={onAdd} />
            <ForwardCheckBox bool={forward} onChange={onFowardChange} />
        </List>
    </React.Fragment>
};


export default VipEditableList;