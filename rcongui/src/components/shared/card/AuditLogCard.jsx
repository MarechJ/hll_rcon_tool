import {
  Card,
  CardContent,
  CardHeader,
  Stack,
  Typography,
  Box,
} from "@mui/material";
import dayjs from "dayjs";
import { CodeBlock } from "@/components/shared/CodeBlock";
import { auditDetails } from "@/pages/records/audit-logs/parse";

/**
 * @typedef {Object} AuditLog
 * @property {number} id
 * @property {string} username
 * @property {string} creation_time
 * @property {string} command
 * @property {string} command_arguments
 * @property {string} command_result
 */

/**
 * @typedef {Object} AuditLogCardProps
 * @property {AuditLog} auditLog
 */

/**
 * AuditLogCard component
 *
 * @param {AuditLogCardProps} props - The audit log object
 * @returns {JSX.Element} The AuditLogCard component
 */
export const AuditLogCard = ({ auditLog, ...props }) => {
  const prettyLine = (label, value) => {
    return (
      <Typography>
        {label}:{" "}
        <Box
          component="span"
          sx={{ fontWeight: "bold", bgColor: "background.paper" }}
        >
          {value}
        </Box>
      </Typography>
    );
  };

  return (
    <Card {...props}>
      <CardHeader title={"Audit Log Details"} sx={{ mb: 2 }} />
      <CardContent>
        {auditLog ? (
          <Stack spacing={1}>
            {prettyLine("ID", auditLog.id)}
            {prettyLine("Action", auditLog.command)}
            {prettyLine(
              "Status",
              auditDetails(auditLog).failed ? "Failed" : "Success"
            )}
            {auditDetails(auditLog).error &&
              prettyLine("Error", auditDetails(auditLog).error)}
            {prettyLine("User", auditLog.username)}
            {prettyLine(
              "Time",
              dayjs(auditLog.creation_time).format("MMM D, YYYY h:mm:ss A")
            )}
            {prettyLine(
              "UTC Time",
              dayjs(auditLog.creation_time)
                .utc()
                .format("MMM D, YYYY h:mm:ss A")
            )}
            <Typography variant="h6">Arguments</Typography>
            <CodeBlock
              text={auditLog.command_arguments}
              sx={{ "& pre": { whiteSpace: "pre", wordBreak: "normal" } }}
            />
            <Typography variant="h6">Result</Typography>
            <CodeBlock
              text={auditLog.command_result}
              sx={{ "& pre": { whiteSpace: "pre", wordBreak: "normal" } }}
            />
          </Stack>
        ) : (
          <Typography>Select an audit log to view details</Typography>
        )}
      </CardContent>
    </Card>
  );
};
