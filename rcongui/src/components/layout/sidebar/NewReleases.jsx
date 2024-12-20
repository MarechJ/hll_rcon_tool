import {
  Avatar,
  Box,
  IconButton,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
} from "@mui/material";
import NewReleasesIcon from "@mui/icons-material/NewReleases";
import { useEffect, useState } from "react";
import localforage from "localforage";
import dayjs from "dayjs";
import siteConfig from "@/config/siteConfig";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";

export default function NewReleases() {
  const [releasesStore, setReleasesStore] = useState({
    lastUpdate: null,
    releases: [],
  });

  const [menuAnchor, setMenuAnchor] = useState(null);
  const menuOpen = Boolean(menuAnchor);

  const handleClick = (event) => {
    setMenuAnchor(event.currentTarget);
  };

  const handleClose = () => {
    setMenuAnchor(null);
    setReleasesStore((prevStore) => ({
      lastUpdate: prevStore.lastUpdate,
      releases: prevStore.releases.map((release) => ({
        ...release,
        unread: false,
      })),
    }));
  };

  const unread = releasesStore.releases.reduce((count, release) => {
    return release.unread ? count + 1 : count;
  }, 0);

  useEffect(() => {
    const loadReleases = async () => {
      const storedStore = await localforage.getItem("releases");

      if (
        storedStore &&
        dayjs().diff(dayjs(storedStore.lastUpdate), "hours") < 8
      ) {
        return setReleasesStore(storedStore);
      }

      try {
        const gitResponse = await fetch(
          `https://api.github.com/repos/${siteConfig.repoOwner}/${siteConfig.repoName}/releases`
        );
        if (!gitResponse.ok) throw new Error(gitResponse.statusText);

        let newReleases = await gitResponse.json();

        if (!newReleases.length) throw new Error("No releases found");

        newReleases = newReleases.map((newRelease) => ({
          id: newRelease.id,
          html_url: newRelease.html_url,
          name: newRelease.name,
          published_at: newRelease.published_at,
          body: newRelease.body.slice(0, 100),
          avatar_url: newRelease.author.avatar_url,
          unread:
            storedStore?.releases.find(
              (storedRelease) => storedRelease.id === newRelease.id
            )?.unread ?? true,
        }));

        setReleasesStore({
          lastUpdate: dayjs().format(),
          releases: newReleases.slice(0, 6),
        });
      } catch (error) {
        if (storedStore !== null) {
          return setReleasesStore(storedStore);
        }
      }
    };
    loadReleases();
  }, []);

  useEffect(() => {
    if (releasesStore.releases.length) {
      localforage.setItem("releases", releasesStore);
    }
  }, [releasesStore]);

  return (
    <>
      <ListItem disablePadding sx={{ display: "block" }} onClick={handleClick}>
        <ListItemButton>
          <ListItemIcon>
            <NewReleasesIcon />
          </ListItemIcon>
          <ListItemText
            primary={
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "row",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Box>Releases</Box>
                {unread > 0 && (
                  <Avatar
                    sx={{
                      bgcolor: (theme) => theme.palette.secondary.main,
                      width: "1rem",
                      height: "1rem",
                      fontSize: "0.7rem",
                    }}
                  >
                    {unread}
                  </Avatar>
                )}
              </Box>
            }
          />
        </ListItemButton>
      </ListItem>
      <Menu
        id="releases-menu"
        aria-labelledby="releases-menu"
        anchorEl={menuAnchor}
        open={menuOpen}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
      >
        {releasesStore.releases?.map((release) => (
          <ListItem
            key={release.id}
            sx={{
              "&:hover": {
                cursor: "pointer",
                bgcolor: (theme) => theme.palette.action.hover,
              },
            }}
            onClick={handleClose}
            secondaryAction={
              <IconButton
                href={release.html_url}
                sx={{ width: 32, height: 32 }}
                target="_blank"
              >
                <OpenInNewIcon />
              </IconButton>
            }
          >
            <ListItemAvatar>
              <Avatar src={release.avatar_url} alt={release.name} />
            </ListItemAvatar>
            <ListItemText
              sx={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
              primary={`${release.name} @ ${dayjs(release.published_at).format(
                "L"
              )}`}
              secondary={release.body + "..."}
            />
          </ListItem>
        ))}
      </Menu>
    </>
  );
}
