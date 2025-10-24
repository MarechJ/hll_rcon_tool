import { Paper, Tooltip, Chip, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";

const ListItem = styled("li")(({ theme }) => ({
  margin: theme.spacing(0.5),
}));

export const BadgeList = ({ recipients, onDelete }) => {
  const handleDelete = (player) => () => {
    onDelete(player);
  };

  const isEmpty = !recipients || recipients.length === 0

  return (
    <>
      <Paper
        sx={{
          display: "flex",
          justifyContent: "start",
          flexWrap: "wrap",
          listStyle: "none",
          py: 1,
          px: 1.5,
          m: 0,
          my: 2,
          minHeight: 30,
          border: (theme) => `1px solid ${isEmpty ? theme.palette.error.light : theme.palette.divider}`,
        }}
        component="ul"
      >
        {isEmpty && (
          <Typography color="textDisabled">No recipients selected</Typography>
        )}
        {recipients.map(({ recipient, status, label }) => {
          return (
            <ListItem key={recipient.player_id}>
              <Tooltip title={recipient.name}>
                <Chip
                  size="small"
                  label={label}
                  color={status}
                  onDelete={handleDelete(recipient)}
                />
              </Tooltip>
            </ListItem>
          );
        })}
      </Paper>
    </>
  );
};
