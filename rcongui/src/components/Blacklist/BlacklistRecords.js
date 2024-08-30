import {
  Box,
  Button,
  Grid,
  LinearProgress,
} from "@material-ui/core";
import BlacklistRecordsSearch from "./BlacklistRecordsSearch";
import React from "react";
import {
  addPlayerToBlacklist,
  get,
  getBlacklists,
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";
import Pagination from "@material-ui/lab/Pagination";
import BlacklistRecordGrid from "./BlacklistRecordGrid";
import { List, fromJS } from "immutable";
import { BlacklistRecordCreateButton } from "./BlacklistRecordCreateDialog";
import { Skeleton } from "@material-ui/lab";
import { Link } from "react-router-dom";

async function getBlacklistRecords(searchParams) {
  let path = "get_blacklist_records?" + new URLSearchParams(
    Object.entries(searchParams)
      .filter(([_, v]) => v || v === 0)
  );
  const response = await get(path)
  return showResponse(response, "get_blacklist_records")
}

const MyPagination = ({ pageSize, total, page, setPage }) => (
  <Pagination
    count={Math.ceil(total / pageSize)}
    page={page}
    onChange={(e, val) => setPage(val)}
    variant="outlined"
    color="standard"
    showFirstButton
    showLastButton
  />
);

const BlacklistRecords = () => {
  // inital state, first render
  const [isLoading, setIsLoading] = React.useState(true);
  // when fetching loading records
  const [isFetching, setIsFetching] = React.useState(false);
  const [blacklists, setBlacklists] = React.useState([]);
  const [records, setRecords] = React.useState(List());
  const [totalRecords, setTotalRecords] = React.useState(0);
  const [page, setPage] = React.useState(1);
  const [searchQuery, setSearchQuery] = React.useState({
    player_id: undefined,
    reason: undefined,
    blacklist_id: undefined,
    exclude_expired: false,
    page_size: 50,
  });

  React.useEffect(() => {
    if (!blacklists.length) {
      loadBlacklists();
    }
    loadRecords();
  }, [searchQuery, page]);

  async function loadBlacklists() {
    setBlacklists(await getBlacklists());
  }

  async function loadRecords() {
    setIsFetching(true);
    try {
      const data = await getBlacklistRecords({ ...searchQuery, page });
      const records = data.result;
      if (records) {
        setRecords(fromJS(records.records));
        setTotalRecords(records.total);
      }
      setIsFetching(false);
      // delay UI, this can be removed along with skeletons
      await new Promise((res) => setTimeout(res, 500));
      setIsLoading(false);
    } catch (error) {
      handle_http_errors(error);
    }
  }

  async function createRecord(recordDetails) {
    await addPlayerToBlacklist(recordDetails);
    loadRecords();
  }

  // If you don't like the loading skeletons, just return `null`
  if (isLoading) {
    return (
      <Grid container spacing={4} justify="center">
        <Grid item xl={6} xs={12}>
          <Skeleton variant="rect" height={140} />
        </Grid>
        <Grid container item xl={3} xs={12} justify="center" spacing={2}>
          <Grid item xl={12}>
            <Skeleton
              variant="rect"
              width={200}
              height={42}
              style={{ margin: "0 auto", borderRadius: 5 }}
            />
          </Grid>
          <Grid item xl={12}>
            <Skeleton
              variant="rect"
              width={155}
              height={42}
              style={{ margin: "0 auto", borderRadius: 5 }}
            />
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <Skeleton
            variant="rect"
            width={360}
            height={32}
            style={{ margin: "0 auto" }}
          />
        </Grid>
        <Grid item xs={12}>
          <Skeleton variant="rect" height={140} />
        </Grid>
        <Grid item xs={12}>
          <Skeleton
            variant="rect"
            width={360}
            height={32}
            style={{ margin: "0 auto" }}
          />
        </Grid>
      </Grid>
    );
  }

  return (
    <Grid container spacing={4} justify="center">
      <Grid item xl={6} xs={12}>
        <BlacklistRecordsSearch
          blacklists={blacklists}
          onSearch={setSearchQuery}
          disabled={isLoading || isFetching}
        />
      </Grid>
      <Grid item xl={3} xs={12}>
        <Grid
          container
          spacing={3}
          alignContent="center"
          alignItems="center"
          justify="center"
          style={{ paddingTop: 6 }}
        >
          <Grid item xl={12}>
            <BlacklistRecordCreateButton
              blacklists={blacklists}
              onSubmit={createRecord}
            >
              Create New Record
            </BlacklistRecordCreateButton>
          </Grid>
          <Grid item xl={12}>
            <Button
              component={Link}
              to={"/blacklists/manage"}
              variant="contained"
              color="primary"
              size="large"
            >
              Manage Lists
            </Button>
          </Grid>
        </Grid>
      </Grid>
      <Grid item xs={12}>
        <MyPagination
          pageSize={searchQuery.pageSize}
          page={page}
          setPage={setPage}
          total={totalRecords}
        />
      </Grid>
      <Grid item xs={12}>
        {isFetching ? <LinearProgress color="secondary" /> : ""}
        <BlacklistRecordGrid
          blacklists={blacklists}
          records={records}
          onRefresh={loadRecords}
        />
      </Grid>
      <Grid item xs={12}>
        <MyPagination
          pageSize={searchQuery.pageSize}
          page={page}
          setPage={setPage}
          total={totalRecords}
        />
      </Grid>
    </Grid>
  );
};

export default BlacklistRecords;
