import React from "react";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { UnderConstruction } from "@/components/UnderConstruction";
import {
  Avatar,
  Divider,
  IconButton,
  InputBase,
  ListItemAvatar,
  ListItemText,
  ListSubheader,
  MenuItem,
  Paper,
  Select,
  selectClasses,
  Stack,
  styled,
} from "@mui/material";
import DevicesRoundedIcon from "@mui/icons-material/DevicesRounded";
import AddCircleIcon from "@mui/icons-material/AddCircle";

export const loader = async (o) => {
  console.log(o)
  return null;
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
  const [value, setValue] = React.useState("Standard");
  const navigate = useNavigate();

  const handleChange = (event) => {
    setValue(event.target.value);
    navigate(
      messageTypes.find((type) => type.name === event.target.value).href
    );
  };

  return (
    <Stack direction={"column"} sx={{ minWidth: 300 }}>
      <Select
        labelId="messages-select"
        id="messages-simple-select"
        value={value}
        onChange={handleChange}
        displayEmpty
        inputProps={{ "aria-label": "Select messages" }}
        fullWidth
        MenuProps={{
          PaperProps: {
            sx: {
              "& .MuiMenuItem-root:not(:last-child)": {
                mb: 1,
              },
            },
          },
        }}
        sx={{
          maxHeight: 56,
          borderBottomLeftRadius: 0,
          borderBottomRightRadius: 0,
          "&.MuiList-root": {
            p: "8px",
          },
          [`& .${selectClasses.select}`]: {
            display: "flex",
            alignItems: "center",
            gap: "2px",
            pl: 1,
          },
        }}
      >
        <ListSubheader sx={{ pt: 0 }}>Messages</ListSubheader>
        {messageTypes?.map((type) => (
          <MenuItem key={type.name} value={type.name}>
            <ListItemAvatar>
              <Avatar alt={type.name}>
                <DevicesRoundedIcon sx={{ fontSize: "1rem" }} />
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              sx={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
              primary={type.name}
            />
          </MenuItem>
        ))}
      </Select>
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
    </Stack>
  );
}

const Messages = () => {
  return (
    <Stack direction={"row"}>
      <Panel />
      <Box sx={{ flexGrow: 1, background: "green", width: "100%" }}>
        <Outlet context={{ hello: "World" }} />
      </Box>
    </Stack>
  );
};

export default Messages;
