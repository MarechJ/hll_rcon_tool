import React from "react";
import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "../../../utils/fetchUtils";
import InputLabel from "@mui/material/InputLabel";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import { Button } from "@mui/material";
import Autocomplete from '@mui/material/Autocomplete';
import TextField from "@mui/material/TextField";
import moment from "moment";
import { List as IList, fromJS } from "immutable";
import Grid from "@mui/material/Grid2";

const AuditLogsTable = ({ auditLogs }) => {
  const [myRowPerPage, setRowPerPage] = React.useState(
    window.localStorage.getItem("auditlogs_row_per_page") || 50
  );
  const saveRowsPerPage = (rowPerPage) => {
    window.localStorage.setItem("auditlogs_row_per_page", rowPerPage);
    setRowPerPage(rowPerPage);
  };
  const columns = [
    {
      name: "creation_time",
      label: "Time",
      options: {
        customBodyRenderLite: (dataIndex) =>
          moment.utc(auditLogs.get(dataIndex)?.get("creation_time")).local().format(
            "ddd Do MMM HH:mm:ss"
          ),
      },
    },
    { name: "username", label: "User name" },
    { name: "command", label: "Command" },
    { name: "command_arguments", label: "Command Parameters" },
    { name: "command_result", label: "Command Result" },
  ];

  const options = {
    filter: false,
    rowsPerPage: myRowPerPage,
    selectableRows: "none",
    rowsPerPageOptions: [10, 25, 50, 100, 250, 500, 1000],
    onChangeRowsPerPage: saveRowsPerPage,
  };

  return (
    (<Grid container justifyContent="center">
      <Grid>
      {"Audit logs"}
      </Grid>
    </Grid>)
  );
};

const AuditLog = () => {
  const [auditLogs, setAuditLogs] = React.useState(new IList());
  const [usernames, setUsernames] = React.useState(new IList());
  const [commands, setCommands] = React.useState(new IList());
  const [usernameSearch, setUsernameSearch] = React.useState([]);
  const [commandSearch, setCommandSearch] = React.useState([]);
  const [paramSearch, setParamSearch] = React.useState("");
  const [timeSort, setTimeSort] = React.useState("desc");

  const getAuditLogs = () => {
    get("get_audit_logs?" + new URLSearchParams({
      usernames: usernameSearch,
      commands: commandSearch,
      parameters: paramSearch,
      time_sort: timeSort,
    }))
      .then((res) => showResponse(res, "get_audit_logs", false))
      .then((res) => {
        setAuditLogs(fromJS(res.result));
      });
  };

  const getMetdata = () => {
    get("get_audit_logs_autocomplete")
      .then((res) => res.json())
      .then((res) => {
        if (res) {
          if (res.result?.usernames) {
            setUsernames(fromJS(res.result.usernames));
          }
          if (res.result?.commands) {
            setCommands(fromJS(res.result.commands));
          }
        }
      })
      .catch(handle_http_errors);
  };

  React.useEffect(() => {
    getMetdata();
    getAuditLogs();
  }, []);

  return (
    (<Grid
        container
        spacing={2}
        justifyContent="flex-start"
        alignItems="center"
      >
      <Grid size={3}>
        <Autocomplete
          multiple
          clearOnEscape
          id="tags-outlined"
          options={usernames.toJS()}
          value={usernameSearch}
          filterSelectedOptions
          onChange={(e, val) => {
            setUsernameSearch(val);
          }}
          renderInput={(params) => (
            <TextField
              {...params}
              variant="outlined"
              label="Search for usernames"
              fullWidth
            />
          )}
        />
      </Grid>
      <Grid size={3}>
        <Autocomplete
          multiple
          clearOnEscape
          options={commands.toJS()}
          value={commandSearch}
          filterSelectedOptions
          onChange={(e, val) => {
            setCommandSearch(val);
          }}
          renderInput={(params) => (
            <TextField
              {...params}
              variant="outlined"
              label="Search for commands"
              fullWidth
            />
          )}
        />
      </Grid>
      <Grid>
        <TextField
          label="Parameters search"
          value={paramSearch}
          onChange={(e) => setParamSearch(e.target.value)}
        />
      </Grid>
      <Grid>
        <FormControl>
          <InputLabel htmlFor="age-native-simple">Time sort</InputLabel>
          <Select
            native
            value={timeSort}
            onChange={(e) => setTimeSort(e.target.value)}
            inputProps={{
              name: "age",
              id: "age-native-simple",
            }}
          >
            <option value={"asc"}>Asc</option>
            <option value={"desc"}>Desc</option>
          </Select>
        </FormControl>
      </Grid>
      <Grid>
        <Button variant="contained" onClick={getAuditLogs}>
          Search
        </Button>
      </Grid>
      <Grid size={12}>
        <AuditLogsTable auditLogs={auditLogs} />
      </Grid>
    </Grid>)
  );
};

export default AuditLog;
