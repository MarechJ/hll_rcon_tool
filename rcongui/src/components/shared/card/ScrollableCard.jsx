import React from "react";
import { CardHeader } from "@mui/material";
import PropTypes from "prop-types";
import { BaseCard, ScrollableContent } from "./styles";

/**
 * A card component with scrollable content
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Content to be rendered inside the card
 * @param {string} props.title - Card title
 * @param {number} props.height - Card height in pixels
 * @param {Object} props.sx - Additional styles for the card
 * @returns {JSX.Element} Rendered component
 */
const ScrollableCard = ({ children, title, height = 250, sx = {} }) => {
  return (
    <BaseCard sx={{ height, ...sx }}>
      <CardHeader 
        title={title} 
        titleTypographyProps={{ variant: "h6" }} 
      />
      <ScrollableContent sx={{ maxHeight: height - 75 }}>
        {children}
      </ScrollableContent>
    </BaseCard>
  );
};

ScrollableCard.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string.isRequired,
  height: PropTypes.number,
  sx: PropTypes.object,
};

export default ScrollableCard;
