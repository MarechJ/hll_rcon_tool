import "react-toastify/dist/ReactToastify.css";
import Grid from "@mui/material/Grid2";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "@/utils/fetchUtils";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import throttle from "lodash/throttle";
import {Component, Fragment} from "react";

export class LoginBox extends Component {
  constructor(props) {
    super(props);

    this.state = {
      username: "",
      password: "",
      open: false,
      isLoggedIn: false,
      interval: null,
    };

    this.login = this.login.bind(this);
    this.logout = this.logout.bind(this);
    this.isLoggedIn = this.isLoggedIn.bind(this);
  }

  componentDidMount() {
    const f = throttle(this.isLoggedIn, 1000 * 55);
    this.isLoggedIn();
    this.setState({
      interval: setInterval(f, 1000 * 60),
    });
  }

  componentWillUnmount() {
    clearInterval(this.state.interval);
  }

  isLoggedIn() {
    return get("is_logged_in")
      .then((response) => response.json())
      .then((res) => this.setState({ isLoggedIn: res.result.authenticated }))
      .catch(handle_http_errors);
  }

  login() {
    return postData(`${process.env.REACT_APP_API_URL}login`, {
      username: this.state.username,
      password: this.state.password,
    })
      .then((res) => showResponse(res, `login ${this.state.username}`, true))
      .then((data) => {
        if (data.failed === false) {
          this.setState({ isLoggedIn: true, open: false, password: "" });
        }
      })
      .catch(handle_http_errors);
  }

  logout() {
    return get("logout")
      .then(this.setState({ isLoggedIn: false }))
      .catch(handle_http_errors);
  }

  render() {
    const { open, username, password, isLoggedIn } = this.state;

    return (
      <Fragment>
        <Button
          color="inherit"
          onClick={() =>
            isLoggedIn === true ? this.logout() : this.setState({ open: true })
          }
        >
          {isLoggedIn === true ? "Logout" : "Login"}
        </Button>
        <Dialog open={open} aria-labelledby="form-dialog-title">
          <DialogTitle id="form-dialog-title">Moderator login</DialogTitle>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              this.login();
            }}
          >
            <DialogContent>
              <Grid container spacing={1}>
                <Grid>
                  <TextField
                    autoFocus
                    size="small"
                    value={username}
                    onChange={(e) => this.setState({ username: e.target.value })}
                    label="Username"
                    variant="standard"
                  />

                  <TextField
                    size="small"
                    value={password}
                    onChange={(e) => this.setState({ password: e.target.value })}
                    label="Password"
                    inputProps={{ type: "password" }}
                    variant="standard"
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => this.setState({ open: false })} color="primary">
                cancel
              </Button>
              <Button type="submit" color="primary">
                login
              </Button>
            </DialogActions>
          </form>
        </Dialog>
      </Fragment>
    );
  }
}
