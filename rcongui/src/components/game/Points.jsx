import { Avatar, Typography, Box } from "@mui/material";
import { styled } from "@mui/material";

export const NumberText = styled(Typography)(() => ({
  fontSize: "0.8rem",
  fontWeight: "600",
}));

export const SquareIcon = styled((props) => <Avatar variant="square" {...props} />)(({ theme }) => {
  const styles = {
    width: 20,
    height: 20,
  }

  if (theme.palette.mode === "dark") {
    styles.backgroundColor = theme.palette.background.default;
  }
  
  return styles 
});

const Points = ({ value, type, direction = "left" }) => {
  if (direction === "left") {
    return (
      <>
        <SquareIcon variant="square">
          <Box
            component={"img"}
            src={`/icons/metrics/${type}.png`}
            width={16}
            height={16}
            alt={type}
          />
        </SquareIcon>
        <NumberText>{value ?? 0}</NumberText>
      </>
    );
  }

  if (direction === "right") {
    return (
      <>
        <NumberText>{value ?? 0}</NumberText>
        <SquareIcon variant="square">
          <Box
            component={"img"}
            src={`/icons/metrics/${type}.png`}
            width={16}
            height={16}
            alt={type}
          />
        </SquareIcon>
      </>
    );
  }
};

export default Points;
