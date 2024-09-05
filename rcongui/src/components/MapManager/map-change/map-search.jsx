import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import InputBase from "@material-ui/core/InputBase";
import Divider from "@material-ui/core/Divider";
import IconButton from "@material-ui/core/IconButton";
import SearchIcon from "@material-ui/icons/Search";
import { Box, Chip } from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
  root: {
    padding: "2px 4px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    [theme.breakpoints.up("sm")]: {
      flexDirection: "row",
    },
  },
  search: {
    display: "flex",
    alignItems: "center",
    justifyContent: "start",
    width: "100%",
  },
  input: {
    marginLeft: theme.spacing(1),
    flex: 1,
  },
  iconButton: {
    padding: 10,
  },
  divider: {
    height: 28,
    margin: 4,
  },
  smDivider: {
    width: "100%",
    [theme.breakpoints.up("sm")]: {
      display: "none",
    },
  },
  chips: {
    display: "flex",
    width: "100%",
    gap: 4,
    paddingTop: 8,
    paddingBottom: 8,
    justifyContent: "start",
    alignItems: "start",
    [theme.breakpoints.up("sm")]: {
      flexDirection: "row",
      width: "auto",
      paddingBottom: 0,
      paddingTop: 0,      
    },
  },
}));

export default function MapSearch({ onChange, onSearch, onFilter, filters }) {
  const classes = useStyles();

  return (
    <Paper className={classes.root}>
      <Box className={classes.search}>
        <IconButton
          className={classes.iconButton}
          aria-label="search"
          onClick={onSearch}
        >
          <SearchIcon />
        </IconButton>
        <Divider className={classes.divider} orientation="vertical" />
        <InputBase
          className={classes.input}
          placeholder="Search Map"
          inputProps={{ "aria-label": "search maps" }}
          onChange={onChange}
        />
        <Divider className={classes.divider} orientation="vertical" />
      </Box>
      <Divider className={classes.smDivider} orientation="horizontal" />
      <Box className={classes.chips}>
        {Object.entries(filters)?.map(([filter, isApplied]) => (
          <Chip
            key={filter}
            size="small"
            label={filter}
            color={isApplied ? "primary" : "default"}
            onClick={() => onFilter(filter)}
          />
        ))}
      </Box>
    </Paper>
  );
}
