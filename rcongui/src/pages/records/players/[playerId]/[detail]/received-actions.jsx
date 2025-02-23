import { useLoaderData } from "react-router-dom";
import { FilterSection, ScrollableContent, ListItem } from "../styled";
import { TextField, MenuItem, Typography } from "@mui/material";
import dayjs from "dayjs";
import { useState } from "react";

const formatDate = (dateString) => {
  return dayjs(dateString).format("lll");
};

const ReceivedActions = () => {
  const { profile } = useLoaderData();
  const [filters, setFilters] = useState({
    actions: {
      search: "",
      type: "",
    },
  });

  const handleFilterChange = (key, subKey, value) => {
    setFilters((prev) => ({ ...prev, [key]: { ...prev[key], [subKey]: value } }));
  };

  const filteredActions = profile.received_actions.filter((item) => {
    const searchLower = filters.actions.search.toLowerCase();
    return (
      item.action_type.includes(filters.actions.type) &&
      (item.reason.toLowerCase().includes(searchLower) || item.by.toLowerCase().includes(searchLower))
    );
  });

  return (
    <div>
      <FilterSection>
        <TextField
          label="Search actions"
          value={filters.actions.search}
          onChange={(e) =>
            handleFilterChange("actions", "search", e.target.value)
          }
          size="small"
        />
        <TextField
          select
          label="Action Type"
          value={filters.actions.type}
          onChange={(e) =>
            handleFilterChange("actions", "type", e.target.value)
          }
          size="small"
        >
          <MenuItem value="">All</MenuItem>
          <MenuItem value="TEMPBAN">TEMPBAN</MenuItem>
          <MenuItem value="PERMABAN">PERMABAN</MenuItem>
          <MenuItem value="PUNISH">PUNISH</MenuItem>
          <MenuItem value="KICK">KICK</MenuItem>
          <MenuItem value="MESSAGE">MESSAGE</MenuItem>
        </TextField>
      </FilterSection>
      <ScrollableContent>
        {filteredActions.map(
          (action, index) => (
            <ListItem key={index}>
              <Typography variant="subtitle1">{action.action_type}</Typography>
              <Typography>Reason: {action.reason}</Typography>
              <Typography>By: {action.by}</Typography>
              <Typography>Time: {formatDate(action.time)}</Typography>
            </ListItem>
          )
        )}
      </ScrollableContent>
    </div>
  );
};

export default ReceivedActions;
