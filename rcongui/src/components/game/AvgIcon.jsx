import { SvgIcon } from "@mui/material";

const AvgIcon = (props) => (
  <SvgIcon {...props}>
    <text
      x="50%"
      y="50%"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize="10"
      fontWeight="bold"
    >
      AVG
    </text>
  </SvgIcon>
);

export default AvgIcon;
