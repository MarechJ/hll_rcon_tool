import React, {useEffect, useRef, useState} from "react";
import Badge from "@material-ui/core/Badge";
import {Comment, Send} from "@material-ui/icons";
import {Box, Button, Chip, Drawer, Grid, makeStyles, TextField} from "@material-ui/core";
import IconButton from "@material-ui/core/IconButton";
import Typography from "@material-ui/core/Typography";
import moment from "moment";

const useStyles = makeStyles((theme) => ({
  message: {
    whiteSpace: "pre-wrap",
    marginTop: '5px',
    marginBottom: '5px',
  },
  date: {
    color: theme.palette.disabledColor,
  },
  padding: {
    padding: theme.spacing(1),
    overflow: "auto",
    maxHeight: '68vh'
  },
}));

const AlwaysScrollToBottom = () => {
  const elementRef = useRef();
  useEffect(() => elementRef.current.scrollIntoView());
  return <div ref={elementRef} />;
};

const ChatContent = ({ data, handleMessageSend }) => {
  const classes = useStyles();
  const [comment, setComment] = React.useState("")

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
                  label={<Typography align="left" className={classes.message}>{message.content}</Typography>}
                />
              </Grid>
              <Grid item>
                <Typography
                  variant="caption"
                  display="block"
                  className={classes.date}
                  color="textSecondary"
                >
                 {moment.utc(message.creation_time).local().format("ddd Do MMM HH:mm:ss")} by {message.by}
                </Typography>
              </Grid>
            </Grid>
          </Grid>
        );
      })}

      <Grid item>
        <AlwaysScrollToBottom />
      </Grid>
      </Grid>
        <Grid
          container
          justify="flex-start"
          alignContent="flex-start"
          alignItems="center"
          className={classes.padding}
        >
          <Grid item xs={10}>
            <TextField
              id="message"
              label="Add comment"
              multiline
              variant="outlined"
              fullWidth
              value={comment}
              onChange={e => setComment(e.target.value)}
            />
          </Grid>
          <Grid item xs={2}>
            <Box paddingLeft={1}>
              <Button
                  variant="contained"
                  fullWidth
                  color="secondary"
                  onClick={e => {handleMessageSend(comment); setComment("")}}
              >
                <Send />
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </React.Fragment>
  );
};

const ChatWidget = ({ data, handleMessageSend }) => {
  const classes = useStyles();
  const [open, setOpen] = useState(false);

  const handleChange = (reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(!open);
  };
  // TODO replace with builtin speeddial from MUI
  return (
    <div className={classes.chatPosition}>
      <Badge color="secondary" overlap="circle" badgeContent={data?.length}>
        <Grid container className={classes.shape}>
          <IconButton onClick={handleChange}>
            <Comment style={{ color: "white" }} />
          </IconButton>
        </Grid>
      </Badge>
      <Drawer anchor="right" open={open} onClose={handleChange}>
        <ChatContent
          data={data}
          handleMessageSend={handleMessageSend}
          classes={classes}
        />
      </Drawer>
    </div>
  );
};

export default ChatWidget;
export { ChatWidget, ChatContent };
