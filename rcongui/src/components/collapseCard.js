import React from "react";
import clsx from "clsx";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import {
  IconButton,
  Card,
  CardHeader,
  CardContent,
  Collapse,
} from "@mui/material";

const CollapseCard = ({
  title,
  children,
  onExpand,
  startOpen = false,
}) => {
  const [expanded, setExpanded] = React.useState(false);
  const handleExpandClick = () => {
    setExpanded(!expanded);
    onExpand();
  };

  React.useEffect(() => {
    setExpanded(startOpen);
  }, [startOpen]);

  return (
    (<Card>
      <CardHeader
        title={title}
        action={
          <IconButton
            onClick={handleExpandClick}
            aria-expanded={expanded}
            aria-label="show more"
            size="large">
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        }
      />
      <Collapse in={expanded} unmountOnExit>
        <CardContent>{children}</CardContent>
      </Collapse>
    </Card>)
  );
};

export default CollapseCard;
