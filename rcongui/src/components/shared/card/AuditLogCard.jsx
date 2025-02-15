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
        {label}: <Box component="span" sx={{ fontWeight: "bold", bgColor: "background.paper" }}>
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
            {prettyLine("User", auditLog.username)}
            {prettyLine("Time", dayjs(auditLog.creation_time).format("lll"))}
            {prettyLine("UTC Time", dayjs(auditLog.creation_time).utc().format("lll"))}
            <Typography variant="h6">Arguments</Typography>
            <CodeBlock text={auditLog.command_arguments} />
            <Typography variant="h6">Result</Typography>
            <CodeBlock text={auditLog.command_result} />
          </Stack>
        ) : (
          <Typography>Select an audit log to view details</Typography>
        )}
      </CardContent>
    </Card>
  );
};
