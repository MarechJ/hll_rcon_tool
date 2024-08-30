import React from "react";
import { Link as RouterLink } from "react-router-dom";
import { Avatar, Grid, GridList, GridListTile, IconButton, Link, List as MaterialList, ListItem, ListItemAvatar, ListItemSecondaryAction, ListItemText, Tooltip, Typography, makeStyles } from "@material-ui/core";
import "emoji-mart/css/emoji-mart.css";
import withWidth from "@material-ui/core/withWidth";
import FileCopyIcon from "@material-ui/icons/FileCopy";
import KeyboardArrowDownIcon from "@material-ui/icons/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@material-ui/icons/KeyboardArrowUp";
import AnnouncementIcon from "@material-ui/icons/Announcement";
import { pure } from "recompose";
import makePlayerProfileUrl from "../../utils/makePlayerProfileUrl";
import { getCountry } from "../PlayersHistory/PlayerTile/PlayerHeader";
import { List } from "immutable";
import moment from "moment";
import BlacklistRecordActionRow from "./BlacklistRecordActionRow";
import BlacklistRecordCreateDialog from "./BlacklistRecordCreateDialog";
import { handle_http_errors, postData, showResponse } from "../../utils/fetchUtils";

const useStyles = makeStyles((theme) => ({
  paperTile: {
    backgroundColor: theme.palette.background.paper,
    minHeight: "100%",
    padding: theme.spacing(2),
  },
  root: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "space-around",
    overflow: "hidden",
  },
}));

const BlacklistRecordTile = ({
  record,
  onEdit,
  onExpire,
  onDelete,
}) => {
  const [showAll, setShowAll] = React.useState(false);
  const [isExpired, setIsExpired] = React.useState(!record.get("is_active"));
  const [expiresAt, setExpiresAt] = React.useState(
    record.get("expires_at") ? moment(record.get("expires_at")) : null
  );

  const expiresAt = record.get("expires_at") ? moment(record.get("expires_at")) : null
  const isExpired = !record.get("is_active")
  const player = record.get("player");
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

  const reason = record.get("formatted_reason")
  const createdAt = moment(record.get("created_at"));
  const now = moment();

  function getReportTemplate() {
    const template =
      `Name: ${firstName || ""
      }\nPlayer ID: ${player.get("player_id")
      }\nSteam URL: ${makePlayerProfileUrl(player.get("player_id"), firstName) || "Unknown"
      }\nType of issue:\nDescription:\nEvidence:`;
    return template;
  }

  return (
    <Grid
      container
      style={isExpired ? { background: "linear-gradient(rgba(0, 0, 0, 0.05), rgba(0, 0, 0, 0.05))" } : {}}
      direction="column"
      justify="space-between"
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
              <React.Fragment>
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
              </React.Fragment>
            }
            secondary={
              <Link
                color="inherit"
                component={RouterLink}
                to={`/player/${player.get("player_id")}`}
              >
                {player.get("player_id")}
              </Link>
            }
          />
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
                    var text = player.get("player_id");
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
            <Tooltip title="Copy report template to clipboard">
              <Typography variant="body2">
                <IconButton
                  size="small"
                  style={{ cursor: "pointer" }}
                  onClick={() => {
                    const text = getReportTemplate();
                    if (navigator.clipboard === undefined) {
                      alert(`This feature only works if your rcon uses HTTPS.`);
                      return;
                    }
                    if (navigator.clipboard === undefined) {
                    } else {
                      navigator.clipboard.writeText(text).then(
                        function () {
                          console.log(
                            "Async: Copying to clipboard was successful!"
                          );
                        },
                        function (err) {
                          console.error("Async: Could not copy text: ", err);
                        }
                      );
                    }
                  }}
                >
                  <AnnouncementIcon fontSize="small" />
                </IconButton>
              </Typography>
            </Tooltip>
          </ListItemSecondaryAction>
        </ListItem>
      </MaterialList>
      <Typography variant={reason.length > 65 ? "body2" : "body1"}>
        {reason.length > 110
          ? reason.substring(0, 108) + "..."
          : reason
        }
      </Typography>
      <Grid
        container
        justify="space-between"
        spacing={0}
        
      >
        <Grid
          container
          justify="space-around"
          spacing={0}
          
        >
          <Grid item>
            <Tooltip title={createdAt.format("LLLL")} arrow>
              <small>
                Banned {moment.duration(now.diff(createdAt)).humanize()} ago
                {record.get("admin_name") ? ` by ${record.get("admin_name")}` : ""}
              </small>
            </Tooltip>
          </Grid>
          <Grid item>
            <Tooltip title={expiresAt ? expiresAt.format("LLLL") : "Permanent"} arrow>
              <small>
                {expiresAt
                  ? (
                    now.isBefore(expiresAt)
                      ? `Expires in ${moment.duration(now.diff(expiresAt)).humanize()}`
                      : `Expired ${moment.duration(now.diff(expiresAt)).humanize()} ago`
                  )
                  : `Never expires`
                }
              </small>
            </Tooltip>
          </Grid>
        </Grid>
        <BlacklistRecordActionRow
          isExpired={isExpired}
          onEdit={() => onEdit(record)}
          onExpire={() => {
            onExpire(record);
          }}
          onDelete={() => onDelete(record)}
        />
      </Grid>
    </Grid>
  )
}

const BlacklistRecordGrid = withWidth()(
  ({
    blacklists,
    records,
    onRefresh,
    width,
  }) => {
    const [editDialogOpen, setEditDialogOpen] = React.useState(false);
    const [editDialogInitialValues, setEditDialogInitialValues] = React.useState();

    function onEditRecord(record) {
      setEditDialogInitialValues({
        recordId: record.get("id"),
        blacklistId: record.get("blacklist").get("id"),
        playerId: record.get("player").get("player_id"),
        expiresAt: record.get("expires_at"),
        reason: record.get("reason"),
      })
      setEditDialogOpen(true);
    }

    function onEditDialogSubmit(data) {
      const recordId = editDialogInitialValues.recordId;
      postData(`${process.env.REACT_APP_API_URL}edit_blacklist_record`, {
        record_id: recordId,
        blacklist_id: data.blacklistId,
        player_id: data.playerId,
        expires_at: data.expiresAt,
        reason: data.reason,
      })
        .then((response) =>
          showResponse(response, `Record ${recordId} was edited`, true)
        )
        .then(result => result && !result.failed && onRefresh())
        .catch(handle_http_errors)
    }

    function onExpireRecord(record) {
      postData(`${process.env.REACT_APP_API_URL}edit_blacklist_record`, {
        record_id: record.get("id"),
        expires_at: moment().utc(),
      })
        .then((response) =>
          showResponse(response, `Record ${record.get("id")} was edited`, true)
        )
        .then(result => result && !result.failed && onRefresh())
        .catch(handle_http_errors)
    }

    function onDeleteRecord(record) {
      postData(`${process.env.REACT_APP_API_URL}delete_blacklist_record`, {
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
    }[width];

    return (
      <React.Fragment>
        <Grid container>
          <Grid item xs={12}>
            <GridList cols={size} cellHeight={210} spacing={12}>
              {records.map((record) => {
                return (
                  <GridListTile
                    key={record.get("id")}
                  >
                    <BlacklistRecordTile
                      
                      record={record}
                      onEdit={onEditRecord}
                      onExpire={onExpireRecord}
                      onDelete={onDeleteRecord}
                    />
                  </GridListTile>
                );
              })}
            </GridList>
          </Grid>
        </Grid>
        <BlacklistRecordCreateDialog
          open={editDialogOpen}
          setOpen={setEditDialogOpen}
          blacklists={blacklists}
          initialValues={editDialogInitialValues}
          onSubmit={onEditDialogSubmit}
          titleText="Edit Blacklist Record"
          submitText="Save"
          disablePlayerId
        />
      </React.Fragment>
    );
  }
);

export default pure(BlacklistRecordGrid);
