import React, { useState, Fragment } from "react";
import { Chip, Menu, MenuItem, Avatar, ListItemIcon, ListItemText } from "@mui/material";
import LinkIcon from "@mui/icons-material/Link";

const EXTERNAL_LINKS = [
  {
    name: "HLL Records",
    urlTemplate: (playerId) => `https://hllrecords.com/profiles/${playerId}`,
    image: "/icons/brands/hllrecords.png",
  },
  {
    name: "HeLO-System",
    urlTemplate: (playerId) => `https://helo-system.de/statistics/players/${playerId}`,
    image: "/icons/brands/helo-system.png",
  },
  {
    name: "HLLoR",
    urlTemplate: (playerId) => `https://hellor.pro/player/${playerId}`,
    image: "/icons/brands/hllor.webp",
  },
  // Add more links here as needed
  // Example:
  // {
  //   name: "Another Site",
  //   urlTemplate: (playerId) => `https://example.com/players/${playerId}`,
  //   image: "/images/icons/brands/example.png",
  // },
];

function LinksChip({ playerId }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLinkClick = (url, event) => {
    event.preventDefault();
    handleClose();
    window.open(url, "_blank", "noopener,noreferrer");
  };

  return (
    <Fragment>
      <Chip
        icon={<LinkIcon />}
        label="Links"
        variant="outlined"
        size="small"
        onClick={handleClick}
        sx={{ "&:hover": { cursor: "pointer" } }}
      />
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        transformOrigin={{ horizontal: "left", vertical: "top" }}
        anchorOrigin={{ horizontal: "left", vertical: "bottom" }}
        sx={{ "& .MuiMenu-list": { padding: 0 } }}
      >
        {EXTERNAL_LINKS.map((link) => {
          const url = link.urlTemplate ? link.urlTemplate(playerId) : link.url;
          return (
            <MenuItem
              key={url}
              onClick={(e) => handleLinkClick(url, e)}
              component="a"
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              sx={{ py: 0.25, px: 1, height: 32 }}
            >
              <ListItemIcon>
                <Avatar
                  src={link.image}
                  alt={link.name}
                  sx={{ width: 20, height: 20 }}
                />
              </ListItemIcon>
              <ListItemText>{link.name}</ListItemText>
            </MenuItem>
          );
        })}
      </Menu>
    </Fragment>
  );
}

export default LinksChip;

