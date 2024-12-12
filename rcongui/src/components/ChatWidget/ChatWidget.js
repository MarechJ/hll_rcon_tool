import {useState} from "react";
import Badge from "@mui/material/Badge";
import {Comment, Send} from "@mui/icons-material";
import {Box, Button, Chip, Drawer, TextField,} from "@mui/material";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import moment from "moment";
import Grid from "@mui/material/Grid2";

const ChatContent = ({data, handleMessageSend}) => {
  const [comment, setComment] = useState("");

  return (<Box paddingLeft={2}>
      <Grid
        container
        justifyContent="flex-start"
        alignContent="flex-start"
        alignItems="flex-end"
        direction="column"
        wrap="nowrap"
      >
        {data?.map((message, index) => {
          return (
            (<Grid key={index}>
              <Grid
                container
                justifyContent="flex-start"
                alignContent="flex-start"
                alignItems="flex-end"
                direction="column"
              >
                <Grid>
                  <Chip
                    style={{height: "auto", paddingTop: "-10px"}}
                    color="primary"
                    label={
                      <Typography align="left">
                        {message.content}
                      </Typography>
                    }/>
                </Grid>
                <Grid>
                  <Typography
                    variant="caption"
                    display="block"

                    color="textSecondary"
                  >
                    {moment
                      .utc(message.creation_time)
                      .local()
                      .format("ddd Do MMM HH:mm:ss")}{" "}
                    by {message.by}
                  </Typography>
                </Grid>
              </Grid>
            </Grid>)
          );
        })}
      </Grid>
      <Grid
        container
        justifyContent="flex-start"
        alignContent="flex-start"
        alignItems="center"

      >
        <Grid size={10}>
          <TextField
            id="message"
            label="Add comment"
            multiline
            fullWidth
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
        </Grid>
        <Grid size={2}>
          <Box paddingLeft={1}>
            <Button
              variant="contained"
              fullWidth
              color="secondary"
              onClick={(e) => {
                handleMessageSend(comment);
                setComment("");
              }}
            >
              <Send/>
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

const ChatWidget = ({data, handleMessageSend}) => {
  const [open, setOpen] = useState(false);

  const handleChange = (reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(!open);
  };
  // TODO replace with builtin speeddial from MUI
  return (
    (<div>
      <Badge color="secondary" overlap="circular" badgeContent={data?.length}>
        <Grid container>
          <IconButton onClick={handleChange} size="large">
            <Comment style={{color: "white"}}/>
          </IconButton>
        </Grid>
      </Badge>
      <Drawer anchor="right" open={open} onClose={handleChange}>
        <ChatContent
          data={data}
          handleMessageSend={handleMessageSend}

        />
      </Drawer>
    </div>)
  );
};

export default ChatWidget;
export {ChatWidget, ChatContent};
