import React, { useEffect, useRef, useState } from "react";
import Badge from "@material-ui/core/Badge";
import { Comment, Send } from "@material-ui/icons";
import {
  Box,
  Button,
  Chip,
  Drawer,
  Grid,
  makeStyles,
  TextField,
} from "@material-ui/core";
import IconButton from "@material-ui/core/IconButton";
import Typography from "@material-ui/core/Typography";
import moment from "moment";

const useStyles = makeStyles((theme) => ({
  message: {
    whiteSpace: "pre-wrap",
    marginTop: "5px",
    marginBottom: "5px",
  },
  date: {
    color: theme.palette.disabledColor,
  },
  padding: {
    padding: theme.spacing(1),
    overflow: "auto",
    maxHeight: "68vh",
  },
}));

const MessageHistory = ({ data }) => {
  const classes = useStyles();
  const [comment, setComment] = React.useState("");

  return (
    <React.Fragment>
      <Box paddingLeft={2}>
        <Grid
          container
          justify="flex-start"
          alignContent="flex-start"
          alignItems="flex-end"
          direction="column"
          className={classes.padding}
          wrap="nowrap"
        >
          {data?.map((message, index) => {
            return (
              <Grid item key={index}>
                <Grid
                  container
                  justify="flex-start"
                  alignContent="flex-start"
                  alignItems="flex-end"
                  direction="column"
                >
                  <Grid item>
                    <Chip
                      style={{ height: "auto", paddingTop: "-10px" }}
                      color="primary"
                      variant="default"
                      label={
                        <Typography align="left" className={classes.message}>
                          {message.reason}
                        </Typography>
                      }
                    />
                  </Grid>
                  <Grid item>
                    <Typography
                      variant="caption"
                      display="block"
                      className={classes.date}
                      color="textSecondary"
                    >
                      {moment
                        .utc(message.time)
                        .local()
                        .format("ddd Do MMM HH:mm:ss")}{" "}
                      by {message.by}
                    </Typography>
                  </Grid>
                </Grid>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    </React.Fragment>
  );
};

export default MessageHistory;
