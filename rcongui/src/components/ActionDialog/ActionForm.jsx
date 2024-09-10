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
  recipients.map((recipient) => {
    let removedClanName = recipient.name.replace(/^\[([^\]]*)\]/, ''); // remove `[clantags]`
    let shortedName = removedClanName.substring(0, 8);
    let label = removedClanName.length > 6 ? shortedName + '...' : shortedName;
    return ({
      recipient: recipient,
      status: recipient.status ?? ACTION_STATUS.default,
      label,
    })
  });

export const ActionForm = ({
  action,
  actionHandlers,
  recipients,
  defaultValues, // not yet used
}) => {

  const {
    handleSubmit,
    control,
    formState: { errors },
    setValue,
  } = useForm();

  const { submitRef, closeDialog, setLoading } = actionHandlers;

  const [recipientStates, setRecipientStates] = React.useState(initRecipients(recipients));
  const [submiting, setSubmiting] = React.useState(false);
  const closeDialogTimeoutRef = React.useRef(null);

  React.useEffect(() => {
    setRecipientStates(initRecipients(recipients));
  }, [recipients]);

  React.useEffect(() => {
    return () => clearTimeout(closeDialogTimeoutRef.current);
  }, [])

  const onSubmit = React.useCallback(async (data) => {
    let allSuccess = true;
    setLoading(true)
    // get list of all selected players and ids
    const steamIds = recipientStates.map(
      ({ recipient }) => recipient.player_id
    );
    const players = recipientStates.map(({ recipient }) => recipient.name);
    // map each to a request payload
    const payloads = [];
    for (let i = 0; i < players.length; i++) {
      payloads.push({ player_name: players[i], player_id: steamIds[i], ...data });
    }
    // now map payloads to requests
    const requests = payloads.map((payload) => action.execute(payload));
    // Update UI to signalize pending state
    setRecipientStates((prevState) =>
      prevState.map((state) => ({
        ...state,
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
      let result, player, player_id;

      if (response.status === 'fulfilled') {
        result = await response.value.json();
        player = result.arguments.player
        player_id = result.arguments.player_id
        console.log({ player, player_id })
        if (!result.failed) {
          idsToStatus[player_id] = ACTION_STATUS.success;
        } else {
          allSuccess = false;
          idsToStatus[player_id] = ACTION_STATUS.error;
        }

      } else {
        allSuccess = false;
        idsToStatus[player_id] = ACTION_STATUS.error;
      }
    }
    // update UI
    setRecipientStates((prevStatePlayers) => {
      return prevStatePlayers.map((state) => {
        const { recipient } = state;
        let nextStatus =
          idsToStatus[recipient.player_id] === ACTION_STATUS.pending
            ? ACTION_STATUS.error
            : idsToStatus[recipient.player_id];

        return {
          ...state,
          status: nextStatus,
        };
      });
    });

    if (allSuccess) {
      setTimeout(closeDialog, 1000)
    } else {
      setLoading(false)
    }
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
