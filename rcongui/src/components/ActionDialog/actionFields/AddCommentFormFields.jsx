import { CommentField } from "../../form/custom/CommentField"

export const AddCommentFormFields = ({ control, errors, ...props }) => {
    return (
        <CommentField control={control} errors={errors} rules={{ required: "Comment is required." }} />
    )
}
