import React from "react";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import { Link, Outlet, useLoaderData, useNavigate } from "react-router-dom";
import { UnderConstruction } from "@/components/UnderConstruction";
import {
  Avatar,
  Divider,
  IconButton,
  InputBase,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemText,
  ListSubheader,
  MenuItem,
  Paper,
  Select,
  selectClasses,
  Stack,
  styled,
  TextField,
} from "@mui/material";
import DevicesRoundedIcon from "@mui/icons-material/DevicesRounded";
import AddCircleIcon from "@mui/icons-material/AddCircle";
import { get, handleHttpError } from "@/utils/fetchUtils";
import { CustomizedDividers } from "../../views/live";

export const loader = async ({ params }) => {
  const { type: messageType } = params;
  const response = await get(`get_standard_${messageType}_messages`);
  handleHttpError(response);
  try {
    const data = await response.json();
    return data.result.messages.map(message => ({
      title: message.slice(0, 16),
      content: message,
    }));
  } catch (error) {
    return [];
  }
};

export const action = async () => {
  return null;
};

const messageTypes = [
  {
    name: "Standard",
    href: "/settings/messages/standard",
  },
  {
    name: "Punishments",
    href: "/settings/messages/punishments",
  },
  {
    name: "Welcome",
    href: "/settings/messages/welcome",
  },
  {
    name: "Broadcast",
    href: "/settings/messages/broadcast",
  },
];

const SearchWrapper = styled(Box)({
  display: "flex",
  alignItems: "center",
  justifyContent: "start",
  width: "100%",
});

const StyledIconButton = styled(IconButton)({
  padding: 10,
});

const StyledDivider = styled(Divider)({
  height: 28,
  margin: 4,
});

function Panel() {
  const data = useLoaderData();

  return (
    <Stack direction={"column"} sx={{ minWidth: 300, width: 300 }}>
      <Paper
        sx={(theme) => ({
          padding: "2px 4px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          borderRadius: 0,
        })}
      >
        <SearchWrapper>
          <InputBase
            sx={(theme) => ({
              marginLeft: theme.spacing(1),
              flex: 1,
            })}
            placeholder="Search Message"
            inputProps={{ "aria-label": "search messages" }}
            onChange={() => {}}
          />
          <StyledDivider orientation="vertical" />
          <StyledIconButton aria-label="search" onClick={() => {}} size="large">
            <AddCircleIcon />
          </StyledIconButton>
        </SearchWrapper>
      </Paper>
      <List>
        {data.map((message) => (
          <ListItemButton>
            <ListItemText
              sx={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
              primary={message.title}
              secondary={message.content}
            />
          </ListItemButton>
        ))}
      </List>
    </Stack>
  );
}

const Messages = () => {
  return (
    <Stack direction={"row"}>
      <Panel />
      <Box sx={{ flexGrow: 1, width: "100%" }}>
        <CustomizedDividers />
        <TextField multiline minRows={16} fullWidth focused />
      </Box>
    </Stack>
  );
};

export default Messages;
