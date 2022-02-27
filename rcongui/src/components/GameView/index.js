import React from "react";
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