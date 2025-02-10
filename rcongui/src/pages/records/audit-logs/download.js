const getLogRow = (log) => {
  return `${log.id},${log.creation_time},${log.username},${log.command},${log.command_arguments},${log.command_result}`;
};

const getLogsTable = (logs) => {
  return logs.map(getLogRow).join("\n");
};

const downloadLogs = (logs) => {
  const csv = getLogsTable(logs);
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "audit_logs.csv";
  a.click();
  URL.revokeObjectURL(url);
};

export default downloadLogs;
