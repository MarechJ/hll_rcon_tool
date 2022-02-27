import React from "react";
import ReactDOM from "react-dom";
import StarIcon from "@material-ui/icons/Star";
import LinearProgress from "@material-ui/core/LinearProgress";
import Switch from "@material-ui/core/Switch";
import FormGroup from "@material-ui/core/FormGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormControl from "@material-ui/core/FormControl";
import MomentUtils from "@date-io/moment";
import { DateTimePicker, MuiPickersUtilsProvider } from "@material-ui/pickers";
import { Bar } from "react-chartjs-2";
import { makeStyles } from "@material-ui/core/styles";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { fromJS } from "immutable";
import {
  Dialog,
  DialogTitle,
  Grid,
  Link,
  Modal,
  Typography,
  DialogContent,
  DialogActions,
  DialogContentText,
  Button,
  TextareaAutosize,
} from "@material-ui/core";


const GameView = ({ classes }) => {
    return <Grid container>
        <Grid item xs={12} md={6}>Team 1</Grid>
        <Grid item xs={12} md={6}>Team 2</Grid>
    </Grid>
}

export default GameView;