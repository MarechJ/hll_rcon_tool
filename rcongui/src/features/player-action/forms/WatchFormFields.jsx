import { ReasonField } from '../fields/ReasonField'

export const WatchFormFields = (props) => {
  return (
    <ReasonField helperText="The reason shown in the discord message upon player connection." {...props} />
  )
};
