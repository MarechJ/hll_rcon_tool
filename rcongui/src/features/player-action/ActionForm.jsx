import { Button } from '@mui/material'
import { useForm } from 'react-hook-form'
import { BadgeList } from './BadgeList'
import { useQueryClient } from '@tanstack/react-query'
import { Fragment, useCallback, useEffect, useRef, useState } from 'react'

const ACTION_STATUS = {
  default: 'default',
  pending: 'warning',
  error: 'error',
  success: 'success'
}

const initRecipients = (recipients) =>
  recipients.map((recipient) => {
    recipient.name = recipient?.name ?? recipient?.profile.names[0]?.name
    let removedClanName = recipient.name.replace(/^\[([^\]]*)\]/, '').trim() // remove `[clantags]`
    let shortedName = removedClanName.substring(0, 8)
    let label = removedClanName.length > 6 ? shortedName + '...' : shortedName
    return {
      recipient: recipient,
      status: recipient.status ?? ACTION_STATUS.default,
      label
    }
  })

export const ActionForm = ({ state: actionState, actionHandlers }) => {
  const {
    handleSubmit,
    formState: { errors },
    ...formProps
  } = useForm({
    // to make the text inputs detect any change when calling
    // setValue from the react-hook-form
    defaultValues: {
      message: '',
      reason: ''
    }
  })
  const { recipients, action } = actionState
  const { submitRef, closeDialog, setLoading, setError } = actionHandlers
  const [recipientStates, setRecipientStates] = useState(initRecipients(recipients))
  const closeDialogTimeoutRef = useRef(null)
  const queryClient = useQueryClient()

  useEffect(() => {
    setRecipientStates(initRecipients(recipients))
  }, [recipients])

  useEffect(() => {
    return () => clearTimeout(closeDialogTimeoutRef.current)
  }, [])

  const onSubmit = useCallback(async (data) => {
    const getPlayerId = (recipient) => recipient.player_id ?? recipient?.profile?.player_id
    let allSuccess = true
    setLoading(true)
    // get list of all selected players and ids
    const steamIds = recipientStates.map(({ recipient }) => getPlayerId(recipient))
    const players = recipientStates.map(({ recipient }) => recipient.name)
    // map each to a request payload
    const payloads = []
    for (let i = 0; i < players.length; i++) {
      payloads.push({ player_name: players[i], player_id: steamIds[i], ...data })
    }
    // now map payloads to requests
    const requests = payloads.map((payload) => action.execute(payload))
    // Update UI to signalize pending state
    setRecipientStates((prevState) =>
      prevState.map((state) => ({
        ...state,
        status: ACTION_STATUS.pending
      }))
    )
    // call requests in parallel
    const responses = await Promise.allSettled(requests)
    // create a map of players' ids and their statuses
    const idsToStatus = recipientStates.reduce((obj, { recipient, status }) => {
      obj[getPlayerId(recipient)] = status
      return obj
    }, {})
    // determine statuses based on the response's return value
    for (const response of responses) {
      let result, player_id
      // if fulfilled it also contains Response object as 'value` param
      if (response.status === 'fulfilled' && response.value.ok) {
        result = await response.value.json()
        player_id = result.arguments.player_id
        if (!result.failed) {
          idsToStatus[player_id] = ACTION_STATUS.success
          // invalidate the player profile query
          queryClient.invalidateQueries({ queryKey: ['player', 'profile', player_id] })
        } else {
          allSuccess = false
          idsToStatus[player_id] = ACTION_STATUS.error
        }
        // otherwise it contains the error object as 'reason' param
      } else {
        allSuccess = false
        // Change this if you want to obtain the message from the server
        // response.value = Response object
        setError(response.reason)
      }
    }
    // update UI
    setRecipientStates((prevStatePlayers) => {
      return prevStatePlayers.map((state) => {
        const { recipient } = state
        let nextStatus =
          idsToStatus[getPlayerId(recipient)] !== ACTION_STATUS.success
            ? ACTION_STATUS.error
            : idsToStatus[getPlayerId(recipient)]

        return {
          ...state,
          status: nextStatus
        }
      })
    })

    if (allSuccess) {
      setTimeout(closeDialog, 1000)
    } else {
      setLoading(false)
    }
  }, [])

  const ActionFields = action.component

  return (
    <Fragment>
      <BadgeList recipients={recipientStates} />
      <form onSubmit={handleSubmit(onSubmit)}>
        <ActionFields errors={errors} {...formProps} {...actionState} />
        <Button ref={submitRef} type='submit' sx={{ display: submitRef && 'none' }}>
          Submit
        </Button>
      </form>
    </Fragment>
  )
}
