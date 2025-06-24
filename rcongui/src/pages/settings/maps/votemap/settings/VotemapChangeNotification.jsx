import { Button } from "@mui/material";

export function VotemapChangeNotification({ closeToast, data }) {
  const acceptChanges = true;
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
        onClick={() => closeToast(acceptChanges)}
      >
        Accept
      </Button>
      <Button
        size="small"
        color="secondary"
        onClick={() => closeToast(!acceptChanges)}
      >
        Ignore
      </Button>
    </div>
  );
}
