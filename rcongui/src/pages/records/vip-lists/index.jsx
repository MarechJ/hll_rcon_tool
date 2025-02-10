import { Button, LinearProgress } from "@mui/material";
import Grid from "@mui/material/Grid2";
import VipListRecordsSearch from "@/components/VipList/VipListRecordsSearch";
import {
  addPlayerToVipList,
  get,
  getVipLists,
  handle_http_errors,
  showResponse,
} from "@/utils/fetchUtils";
import Pagination from "@mui/material/Pagination";
import VipListRecordGrid from "@/components/VipList/VipListRecordGrid";
import { List, fromJS } from "immutable";
import { VipListRecordCreateButton } from "@/components/VipList/VipListRecordCreateDialog";
import { VipListListCreateButton } from "@/components/VipList/VipListListCreateDialog";
import { Skeleton } from "@mui/material";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";

async function getVipListRecords(searchParams) {
  let path =
    "get_vip_list_records?" +
    new URLSearchParams(
      Object.entries(searchParams).filter(([_, v]) => v || v === 0)
    );
  const response = await get(path);
  return showResponse(response, "get_vip_list_records");
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

const VipListRecords = () => {
  // inital state, first render
  const [isLoading, setIsLoading] = useState(true);
  // when fetching loading records
  const [isFetching, setIsFetching] = useState(false);
  const [vipLists, setVipLists] = useState([]);
  const [records, setRecords] = useState(List());
  const [totalRecords, setTotalRecords] = useState(0);
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState({
    player_id: undefined,
    admin_name: undefined,
    is_active: undefined,
    // TODO: expires_at ?
    notes: undefined,
    email: undefined,
    discord_id: undefined,
    vip_list_id: undefined,
    exclude_expired: false,
    page_size: 50,
  });

  useEffect(() => {
    if (!vipLists.length) {
      loadVipLists();
    }
    loadRecords();
  }, [searchQuery, page]);

  async function loadVipLists() {
    setVipLists(await getVipLists());
  }

  async function loadRecords() {
    setIsFetching(true);
    try {
      const data = await getVipListRecords({ ...searchQuery, page });
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
    await addPlayerToVipList(recordDetails);
    loadRecords();
  }

  // If you don't like the loading skeletons, just return `null`
  if (isLoading) {
    return (
      <Grid container spacing={4} justifyContent="center">
        <Grid
          size={{
            xl: 6,
            xs: 12,
          }}
        >
          <Skeleton variant="rectangular" height={140} />
        </Grid>
        <Grid
          container
          justifyContent="center"
          spacing={2}
          size={{
            xl: 3,
            xs: 12,
          }}
        >
          <Grid
            size={{
              xl: 12,
            }}
          >
            <Skeleton
              variant="rectangular"
              width={200}
              height={42}
              style={{ margin: "0 auto", borderRadius: 5 }}
            />
          </Grid>
          <Grid
            size={{
              xl: 12,
            }}
          >
            <Skeleton
              variant="rectangular"
              width={155}
              height={42}
              style={{ margin: "0 auto", borderRadius: 5 }}
            />
          </Grid>
        </Grid>
        <Grid size={12}>
          <Skeleton
            variant="rectangular"
            width={360}
            height={32}
            style={{ margin: "0 auto" }}
          />
        </Grid>
        <Grid size={12}>
          <Skeleton variant="rectangular" height={140} />
        </Grid>
        <Grid size={12}>
          <Skeleton
            variant="rectangular"
            width={360}
            height={32}
            style={{ margin: "0 auto" }}
          />
        </Grid>
      </Grid>
    );
  }

  return (
    <Grid container spacing={4} justifyContent="center">
      <Grid
        size={{
          xl: 6,
          xs: 12,
        }}
      >
        <VipListRecordsSearch
          vipLists={vipLists}
          onSearch={setSearchQuery}
          disabled={isLoading || isFetching}
        />
      </Grid>
      <Grid
        size={{
          xl: 3,
          xs: 12,
        }}
      >
        <Grid
          container
          spacing={3}
          alignContent="center"
          alignItems="center"
          justifyContent="center"
          style={{ paddingTop: 6 }}
        >
          <Grid
            size={{
              xl: 12,
            }}
          >
            <VipListRecordCreateButton
              vipLists={vipLists}
              onSubmit={createRecord}
            >
              Create New Record
            </VipListRecordCreateButton>
          </Grid>
          <Grid
            size={{
              xl: 12,
            }}
          >
            <Button
              component={Link}
              to={"manage"}
              variant="contained"
              color="primary"
              size="large"
            >
              Manage Lists
            </Button>
          </Grid>
        </Grid>
      </Grid>
      <Grid size={12}>
        <MyPagination
          pageSize={searchQuery.pageSize}
          page={page}
          setPage={setPage}
          total={totalRecords}
        />
      </Grid>
      <Grid size={12}>
        {isFetching ? <LinearProgress color="secondary" /> : ""}
        <VipListRecordGrid
          vipLists={vipLists}
          records={records}
          onRefresh={loadRecords}
        />
      </Grid>
      <Grid size={12}>
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

export default VipListRecords;
