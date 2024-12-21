import { Component } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid2 as Grid,
  TextField,
} from "@mui/material";
import { Suspense, lazy } from "react";

const EmojiPicker = lazy(() => import("@emoji-mart/react"));

export class FlagDialog extends Component {
  constructor(props) {
    super(props);
    this.state = {
      flag: null,
      comment: "",
      data: {},
    };
  }

  componentDidMount() {
    import("@emoji-mart/data").then((d) =>
      this.setState((s) => {
        return { ...s, data: d.default };
      })
    );
  }

  render() {
    const { open, handleClose, handleConfirm, SummaryRenderer } = this.props;
    const { flag, comment, data } = this.state;

    return (
      <Dialog open={open} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">
          <SummaryRenderer player={open} flag={flag} />
        </DialogTitle>
        <DialogContent>
          <Grid
            container
            alignContent="center"
            alignItems="center"
            justifyContent="center"
            spacing={2}
          >
            <Grid size={12}>
              <TextField
                label="Comment"
                value={comment}
                onChange={(e) => this.setState({ comment: e.target.value })}
              />
            </Grid>
          </Grid>
          <Grid
            container
            alignContent="center"
            alignItems="center"
            justifyContent="center"
            spacing={2}
          >
            <Grid size={12}>
              <Suspense>
                <EmojiPicker
                  style={{ border: "1px solid red" }}
                  perLine={8}
                  data={data}
                  onEmojiSelect={(emoji) =>
                    this.setState({ flag: emoji.native })
                  }
                />
              </Suspense>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              this.setState({ flag: "" });
              handleClose();
            }}
            color="primary"
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              handleConfirm(open, flag, comment);
              this.setState({ flag: "", comment: "" });
            }}
            color="primary"
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    );
  }
}
