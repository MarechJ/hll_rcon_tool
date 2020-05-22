import React from "react";
import "react-toastify/dist/ReactToastify.css";
import Grid from "@material-ui/core/Grid";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Link from "@material-ui/core/Link";
import Divider from "@material-ui/core/Divider"
import {
    Link as RouterLink
} from "react-router-dom";
import Brightness4Icon from '@material-ui/icons/Brightness4';
import Checkbox from '@material-ui/core/Checkbox';
import Brightness4OutlinedIcon from '@material-ui/icons/Brightness4Outlined';
import ChevronRight from '@material-ui/icons/ChevronRight';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import ServerStatus from './serverStatus'
import { postData, showResponse, get, handle_http_errors } from "../../utils/fetchUtils";
import { toast } from "react-toastify"
import Modal from '@material-ui/core/Modal';
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";


const LoginModal = ({ open, password, username, handleClose, setPassword, setUsername, login }) => (
    <Dialog open={open} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">
            Moderator login
        </DialogTitle>
        <DialogContent>
            <Grid container spacing={1}>
                <Grid item>
                    <TextField size="small" value={username} onChange={e => setUsername(e.target.value)} label="Username" variant="standard" />
                </Grid>
                <Grid item>
                    <TextField size="small" value={password} onChange={e => setPassword(e.target.value)} label="Password" inputProps={{ type: "password" }} variant="standard" />
                </Grid>

            </Grid>
        </DialogContent>
        <DialogActions>
            <Button
                onClick={handleClose}
                color="primary"
            >
                Cancel
      </Button>
            <Button
                onClick={login}
                color="primary"
            >
                login
      </Button>
        </DialogActions>
    </Dialog>
)


export default ({ classes, setSaveDark, dark }) => {
    const [jk, setJk] = React.useState(false)
    const [username, setUsername] = React.useState("")
    const [password, setPassword] = React.useState("")
    const doJk = () => { setSaveDark('<3'); setJk(true) }

    const login = () => (
        // TODO clear password
        postData(`${process.env.REACT_APP_API_URL}login`, { "username": username, "password": password }).then(
            (res) => showResponse(res, `login ${username}`, true)
        ).then(
            data => { if (data.failed === false) { setOpen(false); setPassword("") }}
        ).catch(handle_http_errors)
    )

    const [open, setOpen] = React.useState(false);

    return <Grid container className={classes.grow}>
        <div className={classes.grow}>
            <AppBar position="static" elevation={0} className={classes.appBar}>
                <Toolbar className={classes.toolbar}>
                    <Grid container>
                        <Grid item xs={10}>
                            <Grid container alignContent="flex-start" alignItems="center">
                                <Grid item>
                                    <ServerStatus classes={classes} doJk={doJk} />
                                </Grid>
                                <Grid item className={classes.doublePaddingLeft}></Grid>
                                <Grid item className={classes.doublePaddingLeft}>
                                    <nav className={classes.title}>
                                        <Link
                                            variant="button"
                                            color="inherit"
                                            className={classes.firstLink}
                                            component={RouterLink}
                                            to="/"
                                        >
                                            Live
                                        </Link>
                                        <Link
                                            variant="button"
                                            color="inherit"
                                            className={classes.link}
                                            component={RouterLink}
                                            to="/history"
                                        >
                                            History
                                        </Link>
                                        <Link
                                            variant="button"
                                            color="inherit"
                                            className={classes.link}
                                            component={RouterLink}
                                            to="/settings"
                                        >
                                            Settings
                                        </Link>
                                        <Checkbox icon={<Brightness4Icon />}
                                            checkedIcon={<Brightness4OutlinedIcon />}
                                            checked={dark == "dark" ? true : false} color="default" onChange={(e, val) => !jk ? setSaveDark(val == true ? "dark" : "light") : null} />
                                    </nav>
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item xs={2}>
                            <Grid container className={classes.root} spacing={1} alignContent="flex-start" alignItems="center" justify="flex-end">
                                <Grid item>
                                    <Button variant="outlined" size="medium" onClick={() => setOpen(true)}>Login</Button>
                                </Grid>
                                <Grid item>
                                    <Button variant="outlined" size="medium" onClick={() => get('logout')}>Logout</Button>
                                </Grid>
                            </Grid>
                        </Grid>
                    </Grid>
                </Toolbar>
            </AppBar>
            <LoginModal open={open} handleClose={() => setOpen(false)} login={login} password={password} setPassword={setPassword} username={username} setUsername={setUsername}/>
        </div>
    </Grid>
}