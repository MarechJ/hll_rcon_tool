import { Link as RouterLink } from "react-router-dom";
import {
  Avatar,
  ImageList,
  ImageListItem,
  IconButton,
  Link,
  List as MaterialList,
  ListItem,
  ListItemAvatar,
  ListItemSecondaryAction,
  ListItemText,
  ListItemIcon,
  Tooltip,
  Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import FileCopyIcon from "@mui/icons-material/FileCopy";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import StarIcon from "@mui/icons-material/Star";
import StarBorderIcon from '@mui/icons-material/StarBorder';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ToggleOnIcon from '@mui/icons-material/ToggleOn';
import ToggleOffIcon from '@mui/icons-material/ToggleOff';
import AnnouncementIcon from "@mui/icons-material/Announcement";
import makePlayerProfileUrl from "../../utils/makePlayerProfileUrl";
import { getCountry } from "../PlayersHistory/PlayerTile/PlayerHeader";
import { List } from "immutable";
import moment from "moment";
import VipListRecordActionRow from "./VipListRecordActionRow";
import VipListRecordCreateDialog from "./VipListRecordCreateDialog";
import { handle_http_errors, postData, showResponse } from "@/utils/fetchUtils";
import { Fragment, useState } from "react";

const VipListRecordTile = ({
  record,
  onEdit,
  onActivate,
  onInactivate,
  onDelete,
}) => {
  const [showAll, setShowAll] = useState(false);
  const expiresAt = record.get("expires_at") ? moment(record.get("expires_at")) : null
  const isActive = record.get("is_active")
  const player = record.get("player");
  const email = record.get("player").get('email');
  const discordId = record.get("player").get('discord_id');
  const playerNames = player.get("names", List());
  const firstName = playerNames.get(0) ? playerNames.get(0).get("name") : undefined;
  const firstNameLetter = (firstName || "?")[0];
  const hasMultipleNames = playerNames.size > 1;

  const steamProfile = player.get("steaminfo")
    ? player.get("steaminfo").get("profile")
    : new Map();
  const avatarUrl = steamProfile ? steamProfile.get("avatar") : undefined;
  const country = player.get("steaminfo")
    ? player.get("steaminfo").get("country", "")
    : "";

  const description = record.get('description')
  const notes = record.get('notes')
  const createdAt = moment(record.get("created_at"));
  const now = moment();

  return (
    (<Grid
      container
      style={isActive ? { background: "linear-gradient(rgba(0, 0, 0, 0.05), rgba(0, 0, 0, 0.05))" } : {}}
      direction="column"
      justifyContent="space-between"
    >
      <MaterialList>
        <ListItem component={"div"} alignItems="flex-start" style={{ paddingBottom: 0 }}>
          <ListItemAvatar>
            <Link
              target="_blank"
              color="inherit"
              href={makePlayerProfileUrl(
                player.get("player_id"),
                firstName
              )}
            >
              <Avatar src={avatarUrl}>{firstNameLetter}</Avatar>
            </Link>
          </ListItemAvatar>
          <ListItemText
            primary={
              <Fragment>
                {showAll ? (
                  <Typography variant="body1">
                    {hasMultipleNames ? (
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => setShowAll(false)}
                      >
                        <KeyboardArrowUpIcon fontSize="inherit" />
                      </IconButton>
                    ) : (
                      ""
                    )}
                    {playerNames.map((n) => n.get("name")).join(" | ")}
                  </Typography>
                ) : (
                  <Typography variant="body1">
                    {hasMultipleNames ? (
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => setShowAll(true)}
                      >
                        <KeyboardArrowDownIcon fontSize="inherit" />
                      </IconButton>
                    ) : (
                      ""
                    )}
                    {firstName} {getCountry(country)}
                  </Typography>
                )}
              </Fragment>
            }
            secondary={
              <Link
                color="inherit"
                component={RouterLink}
                to={`/records/players/${player.get("player_id")}`}
              >
                {player.get("player_id")}
              </Link>
            }
          />
          <ListItemIcon>
            {record.get('is_active') ? <ToggleOnIcon /> : <ToggleOffIcon />}
          </ListItemIcon>
          <ListItemSecondaryAction>
            <Tooltip title="Copy Player ID to clipboard">
              <Typography variant="body2">
                <IconButton
                  size="small"
                  style={{ cursor: "pointer" }}
                  onClick={() => {
                    if (navigator.clipboard === undefined) {
                      alert("This feature only works if your rcon uses HTTPS");
                      return;
                    }
                    let text = player.get("player_id");
                    navigator.clipboard.writeText(text).then(
                      function () {
                        console.log("Async: Copying to clipboard was successful!");
                      },
                      function (err) {
                        console.error("Async: Could not copy text: ", err);
                      }
                    );
                  }}
                >
                  <FileCopyIcon fontSize="small" />
                </IconButton>
              </Typography>
            </Tooltip>
          </ListItemSecondaryAction>
        </ListItem>
      </MaterialList>
      <Typography variant={description?.length > 65 ? "body2" : "body1"}>
        {description?.length > 110
          ? description?.substring(0, 108) + "..."
          : description
        }
      </Typography>
      <Typography variant={notes?.length > 65 ? "body2" : "body1"}>
        {notes?.length > 110
          ? notes?.substring(0, 108) + "..."
          : notes
        }
      </Typography>
      {email ? <Typography variant="body1">{email}</Typography> : ""}
      {discordId ? <Typography variant="body1">{discordId}</Typography> : ""}

      <Grid
        container
        justifyContent="space-between"
        spacing={0}
      >
        <Grid
          container
          justifyContent="space-around"
          spacing={0}
        >
          <Grid>
            <Tooltip title={expiresAt ? expiresAt.format("LLLL") : "Permanent"} arrow>
              <small>
                {expiresAt
                  ? (
                    now.isBefore(expiresAt)
                      ? `Expires in ${moment.duration(now.diff(expiresAt)).humanize()} `
                      : `Expired ${moment.duration(now.diff(expiresAt)).humanize()} ago `
                  )
                  : `Never expires `
                }
              </small>
            </Tooltip>
          </Grid>
        </Grid>
        <Grid container justifyContent="space-around" spacing={0}>
          <Grid>
            <Tooltip title='Admin' arrow>
              <small>
                {record.get("admin_name") ? `by ${record.get("admin_name")}` : ""}
              </small>
            </Tooltip>
          </Grid>
        </Grid>
        <VipListRecordActionRow
          isExpired={isActive}
          onEdit={() => onEdit(record)}
          onActivate={() => {
            onActivate(record);
          }}
          onInactivate={() => {
            onInactivate(record);
          }}
          onDelete={() => onDelete(record)}
        />
      </Grid>
    </Grid>)
  );
}

const VipListRecordGrid = ({
  vipLists,
  records,
  onRefresh,
}) => {
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editDialogInitialValues, setEditDialogInitialValues] = useState();

  function onEditRecord(record) {
    setEditDialogInitialValues({
      recordId: record.get("id"),
      playerId: record.get("player").get("player_id"),
      vipListId: record.get("vip_list").get("id"),
      description: record.get("description"),
      active: record.get("active"),
      expiresAt: record.get("expires_at"),
      notes: record.get("notes"),
      email: record.get('player').get('email'),
      discordId: record.get('player').get('discord_id'),
    })
    setEditDialogOpen(true);
  }

  function onEditDialogSubmit(data) {
    const recordId = editDialogInitialValues.recordId;
    postData(`${process.env.REACT_APP_API_URL}edit_vip_list_record`, {
      record_id: recordId,
      vip_list_id: data.vipListId,
      description: data.description,
      active: data.active,
      expires_at: data.expiresAt,
      notes: data.notes,
    })
      .then((response) =>
        showResponse(response, `Record ${recordId} was edited`, true)
      )
      .then(result => result && !result.failed && onRefresh())
      .catch(handle_http_errors)

    /* TODO: this should probably be done separately */
    let payload = {}
    if (data.email) {
      payload.email = data.email
    }
    if (data.discordId) {
      payload.discord_id = data.discordId
    }

    if (Object.keys(payload).length > 0) {
      postData(`${process.env.REACT_APP_API_URL}update_player_profile`, payload).then((response) =>
        showResponse(response, `Player profile updated`, true)
      )
        .then(result => result && !result.failed && onRefresh())
        .catch(handle_http_errors)
    }
  }

  function onActivateRecord(record) {
    postData(`${process.env.REACT_APP_API_URL}edit_vip_list_record`, {
      record_id: record.get("id"),
      active: true,
    })
      .then((response) =>
        showResponse(response, `Record ${record.get("id")} was activated`, true)
      )
      .then(result => result && !result.failed && onRefresh())
      .catch(handle_http_errors)
  }

  function onInactivateRecord(record) {
    postData(`${process.env.REACT_APP_API_URL}edit_vip_list_record`, {
      record_id: record.get("id"),
      active: false,
    })
      .then((response) =>
        showResponse(response, `Record ${record.get("id")} was deactivated`, true)
      )
      .then(result => result && !result.failed && onRefresh())
      .catch(handle_http_errors)
  }

  function onDeleteRecord(record) {
    postData(`${process.env.REACT_APP_API_URL}delete_vip_list_record`, {
      record_id: record.get("id"),
    })
      .then((response) =>
        showResponse(response, `Record ${record.get("id")} was deleted`, true)
      )
      .then(result => result && !result.failed && onRefresh())
      .catch(handle_http_errors)
  }

  const size = {
    xs: 1,
    sm: 2,
    md: 3,
    lg: 4,
    xl: 5,
  }[2];

  return (
    (<Fragment>
      <Grid container>
        <Grid size={12}>
          <ImageList cols={size} cellHeight={210} spacing={12}>
            {records.map((record) => {
              return (
                <ImageListItem
                  key={record.get("id")}
                >
                  <VipListRecordTile
                    record={record}
                    onEdit={onEditRecord}
                    onInactivate={onInactivateRecord}
                    onActivate={onActivateRecord}
                    onDelete={onDeleteRecord}
                  />
                </ImageListItem>
              );
            })}
          </ImageList>
        </Grid>
      </Grid>
      <VipListRecordCreateDialog
        open={editDialogOpen}
        setOpen={setEditDialogOpen}
        vipLists={vipLists}
        initialValues={editDialogInitialValues}
        onSubmit={onEditDialogSubmit}
        titleText="Edit VIP List Record"
        submitText="Save"
        disablePlayerId
      />
    </Fragment>)
  );
}

export default VipListRecordGrid;
