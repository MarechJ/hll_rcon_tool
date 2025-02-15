import { Paper, Tooltip, Chip } from "@mui/material";
import { styled } from "@mui/material/styles";

const ListItem = styled('li')(({ theme }) => ({
  margin: theme.spacing(0.5),
}));

export const BadgeList = ({ recipients }) => {
  return (
    <Paper
      sx={{
        display: 'flex',
        justifyContent: 'start',
        flexWrap: 'wrap',
        listStyle: 'none',
        p: 0.5,
        m: 0,
        my: 2,
      }}
      component="ul"
    >
      {recipients.map(({ recipient, status, label }) => {
        return (
          <ListItem key={recipient.player_id}>
            <Tooltip title={recipient.name}>
              <Chip size="small" label={label} color={status} />
            </Tooltip>
          </ListItem>
        );
      })}
    </Paper>
  );
};
