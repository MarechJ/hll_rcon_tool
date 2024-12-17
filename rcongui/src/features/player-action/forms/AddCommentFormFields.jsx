import { CommentField } from '../fields/CommentField'

export const AddCommentFormFields = (props) => {
  return <CommentField rules={{ required: 'Comment is required.' }} {...props} />
}
