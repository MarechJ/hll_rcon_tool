import React from "react";
import "react-toastify/dist/ReactToastify.css";
import Grid from "@material-ui/core/Grid";
import { showResponse } from "../../utils/fetchUtils";
import { toast } from "react-toastify";

import debounce from 'lodash/debounce'


class ServerStatus extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            name: "",
            nbPlayers: "",
            map: "",
            refreshIntervalSec: 10,
            interval: null
        }

        this.debouncedLoad = debounce(this.load.bind(this), this.state.refreshIntervalSec)
    }

    componentDidMount() {
        this.load()
        this.setState({interval: setInterval(
            this.debouncedLoad, 
            this.state.refreshIntervalSec * 1000)
        })
    }

    componentWillUnmount() {
        clearInterval(this.state.interval)
    }

    async load(command) {
        return fetch(`${process.env.REACT_APP_API_URL}get_status`)
            .then(response => showResponse(response, command))
            .then(data => this.setState({ name: data.result.name, map: data.result.map, nbPlayers: data.result.nb_players }))
            .catch(error => toast.error("Unable to connect to API " + error));
    }

    render() {
        const { map, name, nbPlayers } = this.state
        const { classes } = this.props

        return <React.Fragment>
            <Grid container  alignContent="flex-start" spacing={1}>
                <Grid item xs={12}>
                    <strong style={{ display: "flex" }} className={classes.ellipsis}>{name}</strong>
                </Grid>
                <Grid item xs={12} style={{ display: "flex" }}>
                    <small>{nbPlayers} - {map}</small>
                </Grid>
            </Grid>
        </React.Fragment>
    }
}

export default ServerStatus