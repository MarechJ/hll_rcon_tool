import { Avatar, Typography, Box } from "@mui/material";
import { styled } from "@mui/material";

export const NumberText = styled(Typography)(() => ({
  fontSize: "0.8rem",
  fontWeight: "600",
}));

export const SquareIcon = styled((props) => <Avatar variant="square" {...props} />)(({ theme }) => {
  return {
    width: 20,
    height: 20,
    ...theme.applyStyles("dark", {
      backgroundColor: theme.palette.background.default,
    }),
  };
});

const Points = ({ value, type, direction = "left" }) => {
  if (direction === "left") {
    return (
      <>
        <SquareIcon>
          <Box
            component={"img"}
            src={`/icons/metrics/${type}.png`}
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
            src={`/icons/metrics/${type}.png`}
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
