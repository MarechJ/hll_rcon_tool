import React from "react";
import Grid from "@mui/material/Grid";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Checkbox from "@mui/material/Checkbox";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Divider from "@mui/material/Divider";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";

function not(a, b) {
  return a.filter((value) => b.indexOf(value) === -1);
}

function intersection(a, b) {
  return a.filter((value) => b.indexOf(value) !== -1);
}

const MapRotationTransferList = ({
  availableMaps,
  mapRotation,
  addToRotation,
  removeFromRotation,
}) => {
  const [checked, setChecked] = React.useState([]);

  const leftChecked = intersection(checked, availableMaps);
  const rightChecked = intersection(checked, mapRotation);

  const handleToggle = (value) => () => {
    const currentIndex = checked.indexOf(value);
    const newChecked = [...checked];

    if (currentIndex === -1) {
      newChecked.push(value);
    } else {
      newChecked.splice(currentIndex, 1);
    }

    setChecked(newChecked);
  };

  const handleCheckedRight = () => {
    addToRotation(leftChecked);
    setChecked(not(checked, leftChecked));
  };

  const handleCheckedLeft = () => {
    removeFromRotation(rightChecked);
    setChecked(not(checked, rightChecked));
  };

  const customList = (items, title) => (
    <Paper >
      <h4>{title}</h4>
      <Divider />
      <List dense component="div" role="list">
        {items.map((value) => {
          const labelId = `transfer-list-item-${value}-label`;

          return (
            <ListItem
              key={value}
              role="listitem"
              button
              onClick={handleToggle(value)}
            >
              <ListItemIcon>
                <Checkbox
                  checked={checked.indexOf(value) !== -1}
                  tabIndex={-1}
                  disableRipple
                  inputProps={{ "aria-labelledby": labelId }}
                />
              </ListItemIcon>
              <ListItemText id={labelId} primary={value} />
            </ListItem>
          );
        })}
        <ListItem />
      </List>
    </Paper>
  );

  return (
    (<Grid container spacing={2} justifyContent="center" alignItems="center">
      <Grid item xs={12} sm={5}>
        {customList(availableMaps, "Remaining unused maps")}
      </Grid>
      <Grid item xs={12} sm={2}>
        <Grid container direction="column" alignItems="center">
          <Button
            variant="outlined"
            size="small"
            
            onClick={handleCheckedRight}
            disabled={leftChecked.length === 0}
            aria-label="move selected right"
          >
            <KeyboardArrowDownIcon />
          </Button>
          <Button
            variant="outlined"
            size="small"
            
            onClick={handleCheckedLeft}
            disabled={rightChecked.length === 0}
            aria-label="move selected left"
          >
            <KeyboardArrowUpIcon />
          </Button>
        </Grid>
      </Grid>
      <Grid item xs={12} sm={5}>
        {customList(mapRotation, "Current map rotation")}
      </Grid>
    </Grid>)
  );
};

export default MapRotationTransferList;
