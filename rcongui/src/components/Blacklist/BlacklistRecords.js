import {
  Button,
  Grid,
  LinearProgress,
} from "@material-ui/core";
import useStyles from "../useStyles";
import BlacklistRecordsSearch from "./BlacklistRecordsSearch";
import React from "react";
import { get, handle_http_errors, postData, showResponse } from "../../utils/fetchUtils";
import Pagination from "@material-ui/lab/Pagination";
import BlacklistRecordGrid from "./BlacklistRecordGrid";
import { List, fromJS } from "immutable";
import { BlacklistRecordCreateButton } from "./BlacklistRecordCreateDialog";

const MyPagination = ({ classes, pageSize, total, page, setPage }) => (
  <Pagination
    count={Math.ceil(total / pageSize)}
    page={page}
    onChange={(e, val) => setPage(val)}
    variant="outlined"
    color="standard"
    showFirstButton
    showLastButton
    className={classes.pagination}
  />
);

const BlacklistRecords = ({ classes: globalClasses }) => {
  const classes = useStyles();

  const [isLoading, setIsLoading] = React.useState(false);
  const [blacklists, setBlacklists] = React.useState([]);
  const [records, setRecords] = React.useState(List());
  const [totalRecords, setTotalRecords] = React.useState(0);
  const [page, setPage] = React.useState(1);
  const [searchQuery, setSearchQuery] = React.useState({
    playerId: undefined,
    reason: undefined,
    blacklistId: undefined,
    excludeExpired: false,
    pageSize: 50
  });

  function loadBlacklists() {
    return get("get_blacklists")
      .then((response) => showResponse(response, "get_blacklists", false))
      .then((data) => {
        if (data.result) {
          setBlacklists(data.result);
        }
      })
      .catch(handle_http_errors);
  }
  
  function loadRecords() {
    setIsLoading(true)
    return get("get_blacklist_records?" + new URLSearchParams(Object.entries({
      player_id: searchQuery.playerId,
      reason: searchQuery.reason,
      blacklist_id: searchQuery.blacklistId,
      exclude_expired: searchQuery.excludeExpired,
      page: page,
      page_size: searchQuery.pageSize,
    }).filter(([_, v]) => v && v !== 0)))
      .then((response) => showResponse(response, "get_blacklist_records"))
      .then((data) => {
        setIsLoading(false);
        if (data.result) {
          setRecords(fromJS(data.result.records));
          setTotalRecords(data.result.total);
        }
      })
      .catch(handle_http_errors);
  }

  function createRecord({
    blacklistId,
    playerId,
    expiresAt,
    reason
  }) {
    postData(`${process.env.REACT_APP_API_URL}add_blacklist_record`, {
      blacklist_id: blacklistId,
      player_id: playerId,
      expires_at: expiresAt || null,
      reason
    })
      .then((response) =>
        showResponse(response, `Player ID ${playerId} was blacklisted`, true)
      )
      .catch(handle_http_errors)
      .then(() => loadRecords());
  }

  React.useEffect(() => {
    loadBlacklists();
  }, []);

  React.useEffect(
    () => { setPage(1); },
    [searchQuery]
  );

  React.useEffect(
    () => { loadRecords(); },
    [searchQuery, page]
  );

  return (
    <Grid container spacing={4} justify="center" className={globalClasses.padding}>
      <Grid item xl={6} xs={12}>
        <BlacklistRecordsSearch
          classes={classes}
          blacklists={blacklists}
          onSearch={setSearchQuery}
        />
      </Grid>
      <Grid item xl={3} xs={12}>
        <Grid
          container
          spacing={3}
          alignContent="center"
          alignItems="center"
          justify="center"
          style={{paddingTop: 6}}
        >
          <Grid item xl={12}>
            <BlacklistRecordCreateButton
              blacklists={blacklists}
              onSubmit={createRecord}
            />
          </Grid>
          <Grid item xl={12}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={(e) => {
                e.preventDefault();
                window.location.hash = "#/blacklists/manage";
              }}
            >
              Manage Lists
            </Button>
          </Grid>
        </Grid>
      </Grid>
      <Grid item xs={12}>
        <MyPagination
          classes={classes}
          pageSize={searchQuery.pageSize}
          page={page}
          setPage={setPage}
          total={totalRecords}
        />
      </Grid>
      <Grid item xs={12}>
        {isLoading ? <LinearProgress color="secondary" /> : ""}
        <BlacklistRecordGrid
          classes={classes}
          blacklists={blacklists}
          records={records}
          onRefresh={loadRecords}
        />
      </Grid>
      <Grid item xs={12} className={classes.padding}>
        <MyPagination
          classes={classes}
          pageSize={searchQuery.pageSize}
          page={page}
          setPage={setPage}
          total={totalRecords}
        />
      </Grid>
    </Grid>
  )
}

export default BlacklistRecords