import React, { useEffect, useRef, useState } from "react";
import Badge from "@mui/material/Badge";
import { Comment, Send } from "@mui/icons-material";
import { Box, Button, Chip, Drawer, Grid, TextField } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import moment from "moment";

const MessageHistory = ({ data }) => {
  const [comment, setComment] = React.useState("");

  return (
    (<React.Fragment>
      <Box paddingLeft={2}>
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
              (<Grid item key={index}>
                <Grid
                  container
                  justifyContent="flex-start"
                  alignContent="flex-start"
                  alignItems="flex-end"
                  direction="column"
                >
                  <Grid item>
                    <Chip
                      style={{ height: "auto", paddingTop: "-10px" }}
                      color="primary"
                      label={
                        <Typography align="left" >
                          {message.reason}
                        </Typography>
                      } />
                  </Grid>
                  <Grid item>
                    <Typography
                      variant="caption"
                      display="block"
                      
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
              </Grid>)
            );
          })}
        </Grid>
      </Box>
    </React.Fragment>)
  );
};

export default MessageHistory;
