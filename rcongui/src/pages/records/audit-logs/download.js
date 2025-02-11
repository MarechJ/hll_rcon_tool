const headers = [
  "id",
  "creation_time",
  "username",
  "command",
  "command_arguments",
  "command_result",
];

const getLogRow = (log) => {
  return headers.map((header) => log[header]).join("\t");
};

const getLogsTable = (logs) => {
  let table = "";
  for (const log of logs) {
    table += getLogRow(log) + "\n";
  }
  return table;
};

const downloadLogs = (logs) => {
  const text = getLogsTable(logs);
  const blob = new Blob([text], { type: "text/txt" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "audit_logs.txt";
  a.click();
  URL.revokeObjectURL(url);
};

export default downloadLogs;
