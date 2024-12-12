import {Fragment, useEffect, useState} from "react";
import {
  Stack,
  ListItem,
  ListItemText,
  IconButton,
  List,
  ListItemAvatar,
  Divider,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import { useQueryClient } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";

export const RemoveFlagFormFields = ({ contextData, action, recipients }) => {
  const queryClient = useQueryClient();
  const [flags, setFlags] = useState([]);

  useEffect(() => {
    if (contextData?.profile?.flags) {
      setFlags(contextData?.profile?.flags);
    }
  }, [contextData]);

  return (
    <Stack spacing={2}>
      <List>
        {flags?.map((flag, index) => (
          <Fragment key={flag.id}>
            {index !== 0 && <Divider flexItem variant="inset" />}
            <ListItem
              secondaryAction={
                <IconButton
                  edge="end"
                  aria-label="delete"
                  title="Remove Flag"
                  onClick={async () => {
                    const result = await cmd.UNFLAG_PLAYER({
                      payload: { flag_id: flag.id },
                    });
                    if (!result.failed) {
                      const queryKey = action.context
                        .find((context) => context.type === "profile")
                        ?.getQuery(recipients).queryKey;
                      if (queryKey) {
                        queryClient.invalidateQueries({ queryKey });
                      }
                      setFlags(flags.filter((f) => f.id !== flag.id));
                    }
                  }}
                >
                  <DeleteIcon />
                </IconButton>
              }
            >
              <ListItemAvatar>{flag.flag}</ListItemAvatar>
              <ListItemText primary={flag.comment} secondary={flag.modified} />
            </ListItem>
          </Fragment>
        ))}
        {flags.length === 0 && <ListItem>This player has no flags</ListItem>}
      </List>
    </Stack>
  );
};
