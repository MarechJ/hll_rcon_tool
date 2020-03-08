import React from "react";
import clsx from 'clsx';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import {
  IconButton, Card, CardHeader, CardContent,
  Collapse
} from "@material-ui/core";


const CollapseCard = ({ classes, title, children, onExpand }) => {
    const [expanded, setExpanded] = React.useState(false);
    const handleExpandClick = () => {
      setExpanded(!expanded);
      onExpand();
    };
  
    return <Card>
      <CardHeader title={title} action={
        <IconButton
          className={clsx(classes.expand, {
            [classes.expandOpen]: expanded,
          })}
          onClick={handleExpandClick}
          aria-expanded={expanded}
          aria-label="show more"
        >
          <ExpandMoreIcon />
        </IconButton>
      } />
      <Collapse in={expanded} unmountOnExit>
        <CardContent>
          {children}
        </CardContent>
      </Collapse>
    </Card>
  }
  

  export default CollapseCard;