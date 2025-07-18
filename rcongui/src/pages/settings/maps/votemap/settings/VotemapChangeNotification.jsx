import { Button } from "@mui/material";

export function VotemapChangeNotification({ closeToast, data }) {
  return (
    <div>
      <div>Config has changed</div>
      <ul>
        {data.changes.map((key) => (
          <li key={key}>{key}</li>
        ))}
      </ul>
      <Button
        size="small"
        color="primary"
        onClick={() => {
          if (data.onAccept) data.onAccept();
          closeToast("accept");
        }}
      >
        Accept
      </Button>
      <Button
        size="small"
        color="secondary"
        onClick={() => closeToast("ignore")}
      >
        Ignore
      </Button>
    </div>
  );
}
