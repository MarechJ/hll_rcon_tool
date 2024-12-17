import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import {
  IconButton,
  Card,
  CardHeader,
  CardContent,
  Collapse,
} from "@mui/material";
import {useEffect, useState} from "react";

const CollapseCard = ({
  title,
  children,
  onExpand,
  startOpen = false,
}) => {
  const [expanded, setExpanded] = useState(false);
  const handleExpandClick = () => {
    setExpanded(!expanded);
    onExpand();
  };

  useEffect(() => {
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
