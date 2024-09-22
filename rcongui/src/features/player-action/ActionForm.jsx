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
  state: actionState,
  actionHandlers,
}) => {

  const {
    handleSubmit,
    formState: { errors },
    ...restForm
  } = useForm({
    // to make the text inputs detect any change when calling
    // setValue from the react-hook-form
    defaultValues: {
      message: '',
      reason: '',
    }
  });
  const { recipients, action } = actionState;
  const { submitRef, closeDialog, setLoading, setError } = actionHandlers;
  const [recipientStates, setRecipientStates] = React.useState(initRecipients(recipients));
  const closeDialogTimeoutRef = React.useRef(null);

  React.useEffect(() => {
    setRecipientStates(initRecipients(recipients));
  }, [recipients]);

  React.useEffect(() => {
    return () => clearTimeout(closeDialogTimeoutRef.current);
  }, [])

  const onSubmit = React.useCallback(async (data) => {
    console.log({data})
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
      let result, player_id;
      // if fulfilled it also contains Response object as 'value` param
      if (response.status === 'fulfilled' && response.value.ok) {
        result = await response.value.json();
        player_id = result.arguments.player_id
        if (!result.failed) {
          idsToStatus[player_id] = ACTION_STATUS.success;
        } else {
          allSuccess = false;
          idsToStatus[player_id] = ACTION_STATUS.error;
        }
      // otherwise it contains the error object as 'reason' param 
      } else {
        allSuccess = false;
        // Change this if you want to obtain the message from the server
        // response.value = Response object
        setError(response.reason)
      }
    }
    // update UI
    setRecipientStates((prevStatePlayers) => {
      return prevStatePlayers.map((state) => {
        const { recipient } = state;
        let nextStatus =
          idsToStatus[recipient.player_id] !== ACTION_STATUS.success
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
        <ActionFields errors={errors} {...restForm} {...actionState} />
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
