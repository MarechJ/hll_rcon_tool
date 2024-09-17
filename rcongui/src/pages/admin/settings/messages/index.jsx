import React from "react";
import { Link, Outlet } from "react-router-dom";
import {
  Avatar,
  Box,
  ListItemAvatar,
  ListItemText,
  ListSubheader,
  MenuItem,
  Select,
  selectClasses,
} from "@mui/material";
import DevicesRoundedIcon from "@mui/icons-material/DevicesRounded";

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

const MessagesRoot = () => {
  const [value, setValue] = React.useState("Standard");

  const handleChange = (event) => {
    setValue(event.target.value);
  };

  return (
    <Box>
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
          <MenuItem
            key={type.name}
            value={type.name}
            component={Link}
            href={type.href}
            to={type.href}
          >
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
      <Outlet />
    </Box>
  );
};

export default MessagesRoot;
