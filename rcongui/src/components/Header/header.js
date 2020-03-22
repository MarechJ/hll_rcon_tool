import React from "react";
import "react-toastify/dist/ReactToastify.css";
import Grid from "@material-ui/core/Grid";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Link from "@material-ui/core/Link";
import {
    Link as RouterLink
} from "react-router-dom";
import Brightness4Icon from '@material-ui/icons/Brightness4';
import Checkbox from '@material-ui/core/Checkbox';
import Brightness4OutlinedIcon from '@material-ui/icons/Brightness4Outlined';

import ServerStatus from './serverStatus'

export default ({ classes, setSaveDark, dark }) => (
    <Grid container className={classes.grow}>
        <div className={classes.grow}>
            <AppBar position="static" elevation={0} className={classes.appBar}>
                <Toolbar className={classes.toolbar}>
                    <Grid container alignContent="flex-start" spacing={1}>
                        <Grid item xs={12} md={4} lg={3} xl={2}>
                        <ServerStatus classes={classes} />
                        </Grid>
                        <Grid item className={classes.paddingLeft}>
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
                                    checked={dark ? true : false} color="default" onChange={(e, val) => setSaveDark(val)} />
                            </nav>
                        </Grid>
                    </Grid>
                </Toolbar>
            </AppBar>
        </div>
    </Grid>
)