import React from "react";
import Grid from "@material-ui/core/Grid";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import Checkbox from "@material-ui/core/Checkbox";
import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import Divider from "@material-ui/core/Divider";
import withWidth from "@material-ui/core/withWidth";
import KeyboardArrowUpIcon from "@material-ui/icons/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@material-ui/icons/KeyboardArrowDown";
import KeyboardArrowLeftIcon from "@material-ui/icons/KeyboardArrowLeft";
import KeyboardArrowRightIcon from "@material-ui/icons/KeyboardArrowRight";

function not(a, b) {
  return a.filter((value) => b.indexOf(value) === -1);
}

function intersection(a, b) {
  return a.filter((value) => b.indexOf(value) !== -1);
}

const MapRotationTransferList = ({
  classes,
  availableMaps,
  mapRotation,
  addToRotation,
  removeFromRotation,
  width,
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
    <Paper className={classes.transferList}>
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
    <Grid container spacing={2} justify="center" alignItems="center">
      <Grid item xs={12} sm={5}>
        {customList(availableMaps, "Remaining unused maps")}
      </Grid>
      <Grid item xs={12} sm={2}>
        <Grid container direction="column" alignItems="center">
          <Button
            variant="outlined"
            size="small"
            className={classes.transferListButton}
            onClick={handleCheckedRight}
            disabled={leftChecked.length === 0}
            aria-label="move selected right"
          >
            {width === "xs" ? (
              <KeyboardArrowDownIcon />
            ) : (
              <KeyboardArrowRightIcon />
            )}
          </Button>
          <Button
            variant="outlined"
            size="small"
            className={classes.transferListButton}
            onClick={handleCheckedLeft}
            disabled={rightChecked.length === 0}
            aria-label="move selected left"
          >
            {width === "xs" ? (
              <KeyboardArrowUpIcon />
            ) : (
              <KeyboardArrowLeftIcon />
            )}
          </Button>
        </Grid>
      </Grid>
      <Grid item xs={12} sm={5}>
        {customList(mapRotation, "Current map rotation")}
      </Grid>
    </Grid>
  );
};

export default withWidth()(MapRotationTransferList);
