import { cmd } from "@/utils/fetchUtils";
import {
  Form,
  useLoaderData,
  useNavigation,
  useSubmit,
} from "react-router-dom";
import {
  Autocomplete,
  Box,
  Button,
  FormControl,
  InputLabel,
  LinearProgress,
  MenuItem,
  Select,
  Stack,
  TextField,
  IconButton,
} from "@mui/material";
import { useState } from "react";
import { auditLogsColumns } from "./columns";
import Table from "@/components/table/Table";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
} from "@tanstack/react-table";
import { AuditLogCard } from "@/components/shared/card/AuditLogCard";
import { TableToolbar } from "@/components/table/TableToolbar";
import NavPagination from "@/pages/stats/games/nav-pagination";
import { TablePageSizeSelect } from "@/components/table/TablePageSizeSelect";
import DownloadIcon from "@mui/icons-material/Download";
import downloadLogs from "./download";

/**
 * @typedef {Object} AuditLogResponse
 * @property {AuditLog[]} audit_logs
 * @property {number} page
 * @property {number} page_size
 * @property {number} total_pages
 * @property {number} total_entries
 */

/**
 * @typedef {Object} AuditLogParams
 * @property {string} usernames
 * @property {string} commands
 * @property {string} parameters
 * @property {string} time_sort
 * @property {number} page
 * @property {number} page_size
 */

/**
 * @typedef {Object} AuditLoaderData
 * @property {AuditLog[]} auditLogs
 * @property {number} total_pages
 * @property {number} page
 * @property {AuditLogParams} fields
 */

/**
 * Helper function to get all values from a URL parameter
 *
 * If the parameter is provided without a value, it will be converted to an array with one empty string
 *
 * @param {string[]} value
 * @returns {string[]}
 */
const getAll = (value) => {
  if (Array.isArray(value) && value.length === 1 && value[0] === "") {
    return [];
  }
  return value;
};

/**
 * Loader for the audit logs page.
 *
 * Note: `usernames` and `commands` parameters can be included multiple times
 * which will be converted to an array of strings
 *
 * eg. `?usernames=John&usernames=Jane` will be converted to `["John", "Jane"]`
 *
 * @param {Request} request
 * @returns {Promise<AuditLoaderData>}
 */
export const loader = async ({ request }) => {
  const url = new URL(request.url);

  // Get all values from URL parameters and set defaults
  const usernames = getAll(url.searchParams.getAll("usernames"));
  const commands = getAll(url.searchParams.getAll("commands"));
  const parameters = url.searchParams.get("parameters") ?? "";
  const time_sort = url.searchParams.get("time_sort") ?? "desc";
  const page = url.searchParams.get("page") ?? 1;
  const page_size = url.searchParams.get("page_size") ?? 10;

  const fields = {
    usernames,
    commands,
    parameters,
    time_sort,
    page,
    page_size,
  };

  const params = new URLSearchParams();

  // Cannot use simple Object as some keys can be duplicated for multiple values
  // eg. `usernames` can have multiple values
  Object.entries(fields).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((v) => {
        if (v) params.append(key, v);
      });
    } else if (value !== "" && value !== null) {
      params.append(key, value);
    }
  });

  const auditLogsResult = await cmd.GET_AUDIT_LOGS({ params });
  const autocompleteOptions = await cmd.GET_AUDIT_LOGS_AUTOCOMPLETE();

  return {
    data: auditLogsResult,
    fields,
    autocompleteOptions,
  };
};

// TODO
// - Add pagination
// - Add export
// - Refactor audit log details into a separate component
// - Make the audit log details card collapsible to save space
// - Add a button to copy the audit log details to the clipboard
// - useMemo(columns) to handle column click to show the audit log details

const AuditLogsPage = () => {
  const { data, fields, autocompleteOptions } = useLoaderData();

  const { audit_logs, total_pages, page, page_size } = data;

  const submit = useSubmit();
  const navigation = useNavigation();

  const [formFields, setFormFields] = useState({
    usernames: fields.usernames,
    commands: fields.commands,
    parameters: fields.parameters,
    time_sort: fields.time_sort,
  });

  const [selectedAuditLog, setSelectedAuditLog] = useState(null);

  const table = useReactTable({
    data: audit_logs ?? [],
    columns: auditLogsColumns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    enableRowSelection: true,
    enableMultiRowSelection: false,
    onRowSelectionChange: (updater) => {
      // TODO:
      // This may cause a bug when paginating???
      const newSelection =
        typeof updater === "function" ? updater({}) : updater;
      const selectedId = Object.keys(newSelection)[0];
      const selectedLog = audit_logs[selectedId];
      setSelectedAuditLog(selectedLog);
    },
  });

  const handleInputChange = (e) => {
    const { name, value, checked } = e.target;
    setFormFields((prev) => ({
      ...prev,
      [name]: e.target.type === "checkbox" ? checked : value,
    }));
  };

  const getParams = (otherParams = {}) => {
    const params = new URLSearchParams();
    Object.entries({ ...formFields, ...otherParams }).forEach(
      ([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach((v) => params.append(key, v));
        } else {
          params.append(key, value);
        }
      }
    );
    return params;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    submit(getParams(), { method: "GET" });
  };

  const handlePageSizeChange = (pageSize) => {
    submit(getParams({ page_size: pageSize }), { method: "GET" });
  };

  const handleDownload = () => {
    downloadLogs(audit_logs);
  };

  return (
    <Stack direction={{ xs: "column" }} spacing={1} sx={{ mt: 2 }}>
      <Box sx={{ height: 4 }}>
        {navigation.state === "loading" && (
          <LinearProgress sx={{ height: 4 }} />
        )}
      </Box>

      <Form method="GET" onSubmit={handleSubmit}>
        <Stack spacing={2} direction={{ xs: "column", lg: "row" }}>
          <Autocomplete
            multiple
            sx={{ width: { xs: "100%", lg: "25%" } }}
            clearOnEscape
            limitTags={2}
            id="usernames-autocomplete"
            options={autocompleteOptions.usernames}
            value={formFields.usernames}
            filterSelectedOptions
            onChange={(e, val) => {
              setFormFields((prev) => ({
                ...prev,
                usernames: val,
              }));
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                variant="outlined"
                label="Search by user"
                fullWidth
              />
            )}
          />
          <Autocomplete
            multiple
            sx={{ width: { xs: "100%", lg: "25%" } }}
            clearOnEscape
            limitTags={2}
            id="commands-autocomplete"
            options={autocompleteOptions.commands}
            value={formFields.commands}
            filterSelectedOptions
            onChange={(e, val) => {
              setFormFields((prev) => ({
                ...prev,
                commands: val,
              }));
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                variant="outlined"
                name="commands"
                label="Search by action"
                fullWidth
              />
            )}
          />
          <TextField
            name="parameters"
            sx={{ width: { xs: "100%", lg: "25%" } }}
            value={formFields.parameters}
            onChange={handleInputChange}
            label="Search by parameters"
          />
          <FormControl sx={{ width: { xs: "100%", lg: "15%" } }}>
            <InputLabel id="time-sort-label">Sort by time</InputLabel>
            <Select
              labelId="time-sort-label"
              name="time_sort"
              value={formFields.time_sort}
              onChange={handleInputChange}
              label="Sort by time"
              fullWidth
            >
              <MenuItem value="desc">From newest</MenuItem>
              <MenuItem value="asc">From oldest</MenuItem>
            </Select>
          </FormControl>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            sx={{ width: { xs: "100%", lg: "10%" } }}
            disabled={navigation.state === "loading"}
            onClick={handleSubmit}
          >
            Search
          </Button>
        </Stack>
      </Form>

      <Stack
        component="section"
        id="audit-logs-section"
        spacing={1}
        sx={{ width: "100%" }}
      >
        <Stack direction={{ xs: "column", lg: "row" }} spacing={1}>
          <Stack
            direction="column"
            sx={{
              width: "100%",
              maxWidth: (theme) => theme.breakpoints.values.md,
            }}
          >
            <TableToolbar sx={{ height: 60, px: 1 }}>
              <TablePageSizeSelect
                pageSize={page_size}
                setPageSize={handlePageSizeChange}
              />
              <IconButton
                size="small"
                variant="contained"
                color="primary"
                sx={{
                  "&.MuiIconButton-root": {
                    borderRadius: 0,
                  },
                }}
                onClick={handleDownload}
              >
                <DownloadIcon />
              </IconButton>
              <Box sx={{ flexGrow: 1 }} />
              <NavPagination
                page={page}
                maxPages={total_pages}
                disabled={navigation.state === "loading"}
              />
            </TableToolbar>
            <Table
              table={table}
              columns={auditLogsColumns}
              rowProps={(row) => ({
                onClick: row.getToggleSelectedHandler(),
                sx: {
                  cursor: "pointer",
                  bgcolor: row.getIsSelected() ? "action.selected" : "inherit",
                  "&:hover": {
                    bgcolor: "action.hover",
                  },
                },
              })}
            />
          </Stack>
          <AuditLogCard
            auditLog={selectedAuditLog}
            sx={{
              width: (theme) =>
                theme.breakpoints.down("lg")
                  ? "100%"
                  : theme.breakpoints.values.sm,
            }}
          />
        </Stack>
      </Stack>
    </Stack>
  );
};

export default AuditLogsPage;
