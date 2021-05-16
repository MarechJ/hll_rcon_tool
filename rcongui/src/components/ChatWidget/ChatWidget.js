import React, { useEffect, useRef, useState } from "react";
import Badge from "@material-ui/core/Badge";
import { Comment, Send } from "@material-ui/icons";
import {
  Chip,
  Drawer,
  Grid,
  makeStyles,
  TextField,
  Button,
  Fab
} from "@material-ui/core";
import IconButton from "@material-ui/core/IconButton";
import Typography from "@material-ui/core/Typography";
import moment from "moment";

const useStyles = makeStyles((theme) => ({
  message: {
    whiteSpace: "pre-wrap",
    textAlign: "left"
  },
  date: {
    color: theme.palette.disabledTextColor,
  },
  chatPosition: {
    position: 'fixed',
    right: '2rem',
    bottom: '2rem',
},
padding: {
    padding: theme.spacing(1)
}
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
    <Grid
      container
      justify="flex-start"
      alignContent="flex-start"
      alignItems="flex-start"
      direction="column"
      spacing={1}
      className={classes.padding}
    >
      {data?.map((message, index) => {
        return (
          <Grid item key={index}>
            <Grid
              container
              justify="flex-start"
              alignContent="flex-start"
              alignItems="flex-start"
              direction="column"
            >
              <Grid item xs={12}>
                <Chip
                  style={{ height: "auto" }}
                  variant="body2"
                  color="primary"
                  variant="default"
                  label={<p className={classes.message}>{message.content}</p>}
                />
              </Grid>
              <Grid item xs={12}>
                <Typography
                  variant="caption"
                  display="block"
                  className={classes.date}
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
          alignItems="flex-start"
          spacing={1}
          className={classes.padding}
        >
          <Grid item xs={12}>
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
          <Grid item xs={12}>
            <Button
              variant="contained"
              fullWidth
              color="secondary"
              onClick={e => {handleMessageSend(comment); setComment("")}}
            >
              <Send />
            </Button>
          </Grid>
        </Grid>
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
