import { styled } from "@mui/material/styles";
import { Card, CardHeader, Tabs, Tab, List, ListItem, Divider, Box } from "@mui/material";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import dayjs from "dayjs";
import { logActions } from "@/utils/lib";
import {Fragment, useState} from "react";

// Styled components
const StyledCard = styled(Card)({
  margin: "0 auto",
  width: "100%",
  height: 500,
});

const ScrollableContent = styled("div")({
  maxHeight: 425,
  overflow: "auto",
  padding: 0,
});

const StyledListItem = styled(ListItem)(({ theme }) => ({
  "&:hover": {
    backgroundColor: theme.palette.action.hover,
  },
  transition: theme.transitions.create("background-color"),
  borderRadius: 0,
  padding: theme.spacing(0, 1),
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

/**
 * @typedef {Object} User
 * @property {string} [id] - Unique identifier for the user
 * @property {string} name - Display name of the user
 */

/**
 * @typedef {Object} Log
 * @property {string} message - Message of the log
 * @property {string} timestamp - Timestamp of the log
 * @property {string} action - Type of the log
 * @property {User} user_1 - User who made the log
 * @property {User} user_2 - User who was affected by the log
 */

/**
 * @typedef {Object} LogGroup
 * @property {string} group - Name of the log group
 * @property {Log[]} logs - Array of logs in this group
 */

/**
 * @param {LogGroup[]} logs - Array of log groups
 * @returns {JSX.Element} - Rendered component
 */
const LogsCard = ({ logs }) => {
  const sortedLogs = [...logs].sort((a, b) => a.group.localeCompare(b.group));
  const [selectedTab, setSelectedTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const removePlayerIds = (message) => {
    // Combine both regex patterns into one
    return message.replace(
      /\((?:(?:Axis|Allies)\/)?(?:[0-9]{17}|[A-Z0-9]{16})\)/g,
      ""
    );
  };

  const TIME_FORMAT = "HH:mm:ss, MMM DD";

  // Component to render clickable player names
  const PlayerLink = ({ playerId, children }) => {
    const { openWithId } = usePlayerSidebar();
    const handleClick = () => {
      // Trigger sidebar open with player ID
      // This would need to be implemented based on your sidebar logic
      openWithId(playerId);
    };

    return (
      <span 
        onClick={handleClick}
        style={{ 
          cursor: 'pointer',
          textDecoration: 'underline',
        }}
      >
        {children}
      </span>
    );
  };

  return (
    <StyledCard>
      <CardHeader 
        title="Logs" 
        titleTypographyProps={{ variant: "h6" }} 
      />
      <Tabs
        value={selectedTab}
        onChange={handleTabChange}
        variant="scrollable"
        scrollButtons="auto"
        aria-label="log groups"
      >
        {sortedLogs.map((group, index) => (
          <Tab 
            key={group.group} 
            label={`${logActions[group.group] || ""} ${group.group} (${group.logs.length})`}
          />
        ))}
      </Tabs>
      <ScrollableContent>
        <List disablePadding>
          {sortedLogs[selectedTab]?.logs.map((log, index) => {

            const Message = () => {
              const output = [];
              let message = removePlayerIds(log.message);
              message = message.split(log.user_1?.name);
              // In between each element of the array, add the player link
              message.forEach((part, index) => {
                if (index % 2 === 0) {
                  output.push(<Fragment key={index + "a" + "user_1"}>{part}</Fragment>);
                } else {
                  if (log.user_1?.id) {
                    output.push(<PlayerLink playerId={log.user_1?.id} key={index + "b" + "user_1"}>{log.user_1?.name}</PlayerLink>);
                  } else {
                    output.push(<Fragment key={index + "b" + "user_1"}>{log.user_1?.name}</Fragment>);
                  }
                  output.push(<Fragment key={index + "c" + "user_1"}>{part}</Fragment>);
                }
              });

              if (message[message.length - 1] && message[message.length - 1] !== "") {
                let messageEnd = message[message.length - 1].split(log.user_2?.name);
                output.pop();
                messageEnd.forEach((part, index) => {
                  if (index % 2 === 0) {
                    output.push(<Fragment key={index + "a" + "user_2"}>{part}</Fragment>);
                  } else {
                    if (log.user_2?.id) {
                      output.push(<PlayerLink playerId={log.user_2?.id} key={index + "b" + log.user_2?.id}>{log.user_2?.name}</PlayerLink>);
                    } else {
                      output.push(<Fragment key={index + "b" + log.user_2?.id}>{log.user_2?.name}</Fragment>);
                    }
                    output.push(<Fragment key={index + "c" + log.user_2?.id}>{part}</Fragment>);
                  }
                });

              }

              return <Box sx={{ whiteSpace: "nowrap" }}>{output}</Box>
            }

            return (
              (
                <StyledListItem
                  key={index}
                >
                  <Box component="span" sx={{ width: 125, minWidth: 125 }}>{dayjs.utc(log.timestamp).tz(Intl.DateTimeFormat().resolvedOptions().timeZone).format(TIME_FORMAT)}</Box>
                  <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
                  <Message />
                </StyledListItem>
              )
            )
          })}
        </List>
      </ScrollableContent>
    </StyledCard>
  );
};

export default LogsCard;
