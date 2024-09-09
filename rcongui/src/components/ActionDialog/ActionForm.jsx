import React from 'react';
import { Button } from '@mui/material';
import { useForm } from 'react-hook-form';
import { BadgeList } from './BadgeList';

const ACTION_STATUS = {
  default: 'default',
  pending: 'warning',
  error: 'error',
  success: 'success',
};

const initRecipients = (recipients) =>
  recipients.map((recipient) => ({
    recipient: recipient,
    status: recipient.status ?? ACTION_STATUS.default,
  }));

export const ActionForm = ({
  submitRef,
  action,
  recipients,
  defaultValues, // not yet used
}) => {
  const {
    handleSubmit,
    control,
    formState: { errors },
    setValue,
  } = useForm();

  const [recipientStates, setRecipientStates] = React.useState(
    initRecipients(recipients)
  );

  React.useEffect(() => {
    setRecipientStates(initRecipients(recipients));
  }, [recipients]);

  const onSubmit = React.useCallback(async (data) => {
    // get list of all selected players and ids
    const steamIds = recipientStates.map(
      ({ recipient }) => recipient.player_id
    );
    const players = recipientStates.map(({ recipient }) => recipient.name);
    // map each to a request payload
    const payloads = [];
    for (let i = 0; i < players.length; i++) {
      payloads.push({ player: players[i], player_id: steamIds[i], ...data });
    }
    // now map payloads to requests
    const requests = payloads.map((payload) => action.execute(payload));
    // Update UI to signalize pending state
    setRecipientStates((prevState) =>
      prevState.map(({ recipient }) => ({
        recipient,
        status: ACTION_STATUS.pending,
      }))
    );
    // call requests in parallel
    const responses = await Promise.allSettled(requests);
    // create a map of players' ids and their statuses
    const idsToStatus = recipientStates.reduce((obj, { recipient, status }) => {
      obj[recipient.player_id] = status;
      return obj;
    }, {});
    // determine statuses based on the response's return value
    for (const response of responses) {
      if (response.status === 'fulfilled') {
        const result = await response.value.json();
        const { player, player_id } = result.arguments;
        if (!result.failed) {
          idsToStatus[player_id] = ACTION_STATUS.success;
        } else {
          idsToStatus[player_id] = ACTION_STATUS.error;
        }
      } else {
        idsToStatus[player_id] = ACTION_STATUS.error;
      }
    }
    // update UI
    setRecipientStates((prevStatePlayers) => {
      return prevStatePlayers.map(({ recipient }) => {
        let nextStatus =
          idsToStatus[recipient.player_id] === ACTION_STATUS.pending
            ? ACTION_STATUS.error
            : idsToStatus[recipient.player_id];

        return {
          recipient,
          status: nextStatus,
        };
      });
    });
  }, []);

  const ActionFields = action.component;

  return (
    <React.Fragment>
      <BadgeList recipients={recipientStates} />
      <form onSubmit={handleSubmit(onSubmit)}>
        <ActionFields control={control} errors={errors} setValue={setValue} />
        <Button
          ref={submitRef}
          type="submit"
          sx={{ display: submitRef && 'none' }}
        >
          Submit
        </Button>
      </form>
    </React.Fragment>
  );
};
