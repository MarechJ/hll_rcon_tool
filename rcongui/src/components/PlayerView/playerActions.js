import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import ButtonGroup from '@mui/material/ButtonGroup'
import TextField from '@mui/material/TextField'
import Badge from '@mui/material/Badge'
import Menu from '@mui/material/Menu'
import MenuItem from '@mui/material/MenuItem'
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown'
import 'react-toastify/dist/ReactToastify.css'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogTitle from '@mui/material/DialogTitle'
import { Map } from 'immutable'
import FlagOutlinedIcon from '@mui/icons-material/FlagOutlined'
import TextHistory from '../textHistory'
import Autocomplete from '@mui/material/Autocomplete'
import FormControlLabel from '@mui/material/FormControlLabel'
import Checkbox from '@mui/material/Checkbox'
import { getSharedMessages } from '@/utils/fetchUtils'
import Grid from '@mui/material/Grid2'
import Tooltip from '@mui/material/Tooltip'
import MessageIcon from '@mui/icons-material/Message'
import VisibilityIcon from '@mui/icons-material/Visibility'
import BlockIcon from '@mui/icons-material/Block'
import StarIcon from '@mui/icons-material/Star'
import { Component, Fragment, useState } from 'react'
import range from 'lodash/range'

const Duration = ({ durationNumber, onNumberChange, durationMultiplier, onMultiplierChange }) => (
  <Grid container spacing={1}>
    <Grid>
      <TextField
        style={{ minWidth: '200px' }}
        label='TempBan Duration number'
        type='number'
        shrink
        margin='dense'
        value={durationNumber}
        onChange={(event) => onNumberChange(event.target.value)}
      />
    </Grid>
    <Grid>
      <TextField
        style={{ minWidth: '200px' }}
        select
        value={durationMultiplier}
        onChange={(event) => onMultiplierChange(event.target.value)}
        margin='dense'
        label='TempBan Duration unit'
      >
        <MenuItem key='hours' value={1}>
          hours
        </MenuItem>
        <MenuItem key='days' value={24}>
          days
        </MenuItem>
        <MenuItem key='weeks' value={24 * 7}>
          weeks
        </MenuItem>
        <MenuItem key='months' value={24 * 7 * 4}>
          months
        </MenuItem>
      </TextField>
    </Grid>
  </Grid>
)

class ReasonDialog extends Component {
  constructor(props) {
    super(props)
    this.state = {
      reason: '',
      comment: '',
      saveMessage: true,
      durationNumber: 2,
      durationMultiplier: 1,
      sharedMessages: []
    }

    this.onChange = this.onChange.bind(this)
  }

  componentDidMount() {
    getSharedMessages('punishments').then((data) => this.setState({ sharedMessages: data }))
  }

  onChange(e, value) {
    if (e) {
      e.preventDefault()
    }

    this.setState({ reason: value })
  }

  mapActionToText(actionType, playerName) {
    switch (actionType) {
      case 'watch_player':
        return `Add a watch to ${playerName}`
      case 'punish':
        return `Punish (kill in game) ${playerName}`
      case 'kick':
        return `Kick ${playerName} from the game`
      case 'temp_ban':
        return `Temporary Ban ${playerName}`
      case 'perma_ban':
        return `Permanently Ban ${playerName}`
      case 'message_player':
        return `Message ${playerName}`
      case 'add_blacklist_record':
        return `Add ${playerName} to a blacklist`
      default:
        return ''
    }
  }

  render() {
    const { open, handleClose, handleConfirm } = this.props
    const { reason, comment, saveMessage, sharedMessages, durationNumber, durationMultiplier } = this.state
    const textHistory = new TextHistory('punishments')
    const actionType = open.actionType
    const playerName = open.player
    return (
      <Dialog open={open} aria-labelledby='form-dialog-title'>
        <DialogTitle id='form-dialog-title'>{this.mapActionToText(actionType, playerName)}</DialogTitle>
        <DialogContent>
          <Autocomplete
            freeSolo
            fullWidth
            options={sharedMessages.concat(textHistory.getTexts())}
            inputValue={reason}
            onInputChange={(e, value) => this.onChange(e, value)}
            renderInput={(params) => (
              <TextField
                {...params}
                multiline
                minRows={4}
                maxRows={10}
                label={actionType === 'message_player' ? 'Message' : 'Reason'}
                margin='dense'
                helperText='The message that will be displayed to the player. A message is mandatory'
              />
            )}
          />

          {open.actionType !== 'message_player' ? (
            <TextField
              multiline
              minRows={4}
              maxRows={10}
              fullWidth
              value={comment}
              onChange={(e) => this.setState({ comment: e.target.value })}
              label='Comment'
              margin='dense'
              helperText='A comment that will NOT be displayed to the player'
            />
          ) : (
            ''
          )}
          {open.actionType === 'temp_ban' ? (
            <Duration
              durationNumber={durationNumber}
              onNumberChange={(number) => this.setState({ durationNumber: number })}
              durationMultiplier={durationMultiplier}
              onMultiplierChange={(multiplier) => this.setState({ durationMultiplier: multiplier })}
            />
          ) : (
            ''
          )}
          <FormControlLabel
            control={
              <Checkbox
                checked={saveMessage}
                onChange={() => this.setState({ saveMessage: !saveMessage })}
                color='primary'
              />
            }
            label='Save message as template'
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              this.setState({ reason: '' }, handleClose)
            }}
            color='primary'
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              if (saveMessage) {
                textHistory.saveText(reason, sharedMessages)
              }
              handleConfirm(
                open.actionType,
                open.player,
                reason,
                comment,
                durationMultiplier * durationNumber,
                open.player_id
              )
              this.setState({ reason: '', comment: '' })
            }}
            color='primary'
            disabled={!reason}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    )
  }
}

const PlayerActions = ({
  size,
  handleAction,
  onFlag,
  isWatched,
  displayCount = 3,
  disable = false,
  penaltyCount = Map(),
  disableAll = false,
  onBlacklist,
  onVipDialogOpen
}) => {
  const [anchorEl, setAnchorEl] = useState(null)
  const [isOpen, setOpen] = useState(false)
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget)
    setOpen(true)
  }
  const handleClose = () => {
    setOpen(false)
  }
  const remap_penalties = {
    perma_ban: 'PERMABAN',
    punish: 'PUNISH',
    kick: 'KICK',
    temp_ban: 'TEMPBAN'
  }

  const actions = [
    ['punish', 'PUNISH'],
    ['kick', 'KICK'],
    // ["temp_ban", "TEMP BAN"],
    ['switch_player_now', 'SWITCH'],
    ['switch_player_on_death', 'SWITCH ON DEATH']
    // ["perma_ban", "PERMA BAN"],
  ]
  const show = Math.min(displayCount, actions.length)

  return (
    <Fragment>
      <ButtonGroup size={size} disabled={disableAll} aria-label='small outlined button group'>
        <Tooltip title='Message Player'>
          <Button onClick={() => handleAction('message_player')}>
            <MessageIcon />
          </Button>
        </Tooltip>
        {show > 1 ? (
          <Tooltip title='Watch Player'>
            <Button size='small' onClick={() => handleAction(isWatched ? 'unwatch_player' : 'watch_player')}>
              <VisibilityIcon fontSize='small' />
            </Button>
          </Tooltip>
        ) : (
          ''
        )}
        {range(show).map((idx) => (
          <Button
            key={actions[idx][0]}
            disabled={disable && !actions[idx][0].startsWith('switch')}
            onClick={() => handleAction(actions[idx][0])}
          >
            <Badge size='small' max={9} badgeContent={penaltyCount.get(remap_penalties[actions[idx][0]], 0)}>
              {actions[idx][1]}
            </Badge>
          </Button>
        ))}
        <Tooltip title='Blacklist Player'>
          <Button size='small' onClick={onBlacklist}>
            <BlockIcon fontSize='small' />
          </Button>
        </Tooltip>
        <Tooltip title={"Manage player's VIP"} arrow>
          <Button>
            <StarIcon size='small' onClick={onVipDialogOpen} />
          </Button>
        </Tooltip>
        {onFlag ? (
          <Tooltip title='Flag Player'>
            <Button size='small' onClick={onFlag}>
              <FlagOutlinedIcon fontSize='small' />
            </Button>
          </Tooltip>
        ) : (
          ''
        )}

        {show < actions.length ? (
          <Button disabled={disable} aria-controls='simple-menu' aria-haspopup='true' onClick={handleClick}>
            <ArrowDropDownIcon />
          </Button>
        ) : (
          ''
        )}
      </ButtonGroup>
      {show < actions.length ? (
        <Menu id='simple-menu' anchorEl={anchorEl} keepMounted open={isOpen} onClose={handleClose}>
          {show <= 1 ? (
            <MenuItem size='small' onClick={() => handleAction(isWatched ? 'unwatch_player' : 'watch_player')}>
              <VisibilityIcon fontSize='small' />
            </MenuItem>
          ) : (
            ''
          )}
          {_.range(show, actions.length).map((idx) => {
            const count = penaltyCount.get(remap_penalties[actions[idx][0]], 0)
            return (
              <MenuItem
                key={actions[idx][0]}
                onClick={() => {
                  handleAction(actions[idx][0])
                  handleClose()
                }}
              >
                {actions[idx][1]}
                {count > 0 ? <Chip size='small' color='primary' label={count} /> : ''}
              </MenuItem>
            )
          })}
        </Menu>
      ) : (
        ''
      )}
    </Fragment>
  )
}

export { ReasonDialog, PlayerActions, Duration }
