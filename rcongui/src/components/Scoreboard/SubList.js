import React from "react";
import { Map } from "immutable";
import {
  List,
  ListItem,
  ListItemSecondaryAction,
  ListItemText,
  makeStyles,
  Typography,
  IconButton,
  Collapse,
} from "@material-ui/core";
import ExpandLess from "@material-ui/icons/ExpandLess";
import ExpandMore from "@material-ui/icons/ExpandMore";

const useStyles = makeStyles((theme) => ({
  nested: {
    paddingLeft: theme.spacing(4),
  },
}));

export const SubList =
  ({ playerScore, dataMapKey, title, subtitle, openDefault, sortByKey }) => {
    let data = dataMapKey
      ? playerScore.get(dataMapKey) || new Map()
      : playerScore;
    const styles = useStyles();
    const [open, setOpen] = React.useState(openDefault);

    if (sortByKey)
      data = data.sortBy((v, k) => k)
    else
      data = data.sort().reverse()

    return (
      <React.Fragment>
        <ListItem button onClick={() => setOpen(!open)}>
          <ListItemText
            primary={<Typography variant="h5">{title}</Typography>}
            secondary={subtitle}
          />
          <ListItemSecondaryAction>
            <IconButton onClick={() => setOpen(!open)}>
              {open ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </ListItemSecondaryAction>
        </ListItem>
        <Collapse in={open} timeout="auto" unmountOnExit>
          <List component="div" disablePadding dense>
            {data
              .entrySeq()
              .map(([key, value]) => (
                <ListItem className={styles.nested}>
                  <ListItemText primary={key} />
                  <ListItemSecondaryAction>
                    <Typography variant="h6" color="secondary">
                      {value}
                    </Typography>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
          </List>
        </Collapse>
      </React.Fragment>
    );
  }
