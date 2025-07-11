import { Avatar, Typography, Box } from "@mui/material";
import { styled } from "@mui/material";
import { useTheme } from "@mui/material/styles";

export const NumberText = styled(Typography)(() => ({
  fontSize: "0.8rem",
  fontWeight: "600",
}));

export const SquareIcon = styled((props) => <Avatar variant="square" {...props} />)(({ theme }) => {
  return {
    width: 20,
    height: 20,
    backgroundColor: theme.palette.background.default,
  };
});

const metricSrc = (type, mode) =>
  mode === "light"
    ? `/icons/metrics/${type}_black.png`
    : `/icons/metrics/${type}.png`;

const Points = ({ value, type, direction = "left" }) => {
  const theme = useTheme();
  const mode = theme?.palette?.mode || "light";
  if (direction === "left") {
    return (
      <>
        <SquareIcon>
          <Box
            component={"img"}
            src={metricSrc(type, mode)}
            width={16}
            height={16}
            alt={type}
            title={type}
          />
        </SquareIcon>
        <NumberText>{value ? value.toFixed(0) : 0}</NumberText>
      </>
    );
  }

  if (direction === "right") {
    return (
      <>
        <NumberText>{value ? value.toFixed(0) : 0}</NumberText>
        <SquareIcon variant="square">
          <Box
            component={"img"}
            src={metricSrc(type, mode)}
            width={16}
            height={16}
            alt={type}
            title={type}
          />
        </SquareIcon>
      </>
    );
  }
};

export default Points;
