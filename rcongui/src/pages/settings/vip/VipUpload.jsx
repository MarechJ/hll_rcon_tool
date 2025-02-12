import { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";
import { Alert, Button, Stack, CircularProgress, Typography } from "@mui/material";
import { CloudUpload } from "@mui/icons-material";
import { InputFileUpload } from "@/components/shared/InputFileUpload";
import { vipQueryKeys } from "@/queries/vip-query";

const POLL_INTERVAL = 2000; // 2 seconds

const VipUpload = () => {
  const [showWarning, setShowWarning] = useState(false);
  const [uploadId, setUploadId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const queryClient = useQueryClient();

  const { mutate: uploadVips } = useMutation({
    mutationFn: async (file) => {
      const formData = new FormData();
      formData.append("File", file);

      queryClient.invalidateQueries({ queryKey: [{ queryIdentifier: "vip_upload_status" }] });

      const response = await fetch(
        `${process.env.REACT_APP_API_URL}upload_vips`,
        {
          method: "POST",
          body: formData,
        }
      );
      return response;
    },
    onSuccess: (data) => {
      setUploadId(!data.failed);
    },
    onError: () => {
      setUploadId(null);
    },
  });

  // Poll for upload status
  const { data: uploadStatus } = useQuery({
    queryKey: [{ queryIdentifier: "vip_upload_status" }],
    queryFn: () => cmd.GET_UPLOAD_VIP_FILE_RESPONSE(),
    enabled: !!uploadId,
    refetchInterval: POLL_INTERVAL,
  });

  // Handle status changes with an effect
  useEffect(() => {
    if (!uploadStatus) return;

    switch (uploadStatus.status) {
      case "started":
        setStatus("started");
        break;
      case "finished":
        setTimeout(() => {
          setStatus("finished");
          setResult(uploadStatus.result);
          setUploadId(null);
          queryClient.invalidateQueries({ queryKey: vipQueryKeys.list });
        }, 2000);
        break;
      default:
        break;
    }
  }, [uploadStatus?.status, queryClient]);

  const handleInitialUpload = () => {
    setShowWarning(true);
  };

  const reset = () => {
    setShowWarning(false);
    setStatus(null);
    setUploadId(null);
    setResult(null);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      uploadVips(file);
    }
  };

  if (status === "started") {
    return (
      <Stack spacing={2} alignItems="center">
        <CircularProgress size={24} />
        <Alert severity="info">Processing VIP records... Please wait.</Alert>
      </Stack>
    );
  }

  if (status === "finished") {
    return (
      <Stack spacing={2}>
        <Alert severity="success">VIP records upload finished.</Alert>
        {result?.map((message) => (
          <Typography key={message}>{message}</Typography>
        ))}
        <Button variant="contained" onClick={reset}>
          Confirm
        </Button>
      </Stack>
    );
  }

  if (showWarning) {
    return (
      <Stack spacing={2}>
        <Alert severity="warning">
          This action will override all VIP records for the current server. It
          is recommended to download a backup first.
        </Alert>
        <Stack direction="row" spacing={1}>
          <Button
            fullWidth
            variant="outlined"
            color="error"
            onClick={reset}
          >
            Cancel
          </Button>
          <InputFileUpload
            text="Upload file"
            color="primary"
            variant="contained"
            onChange={handleFileUpload}
            accept=".txt"
            fullWidth
            sx={{ whiteSpace: "nowrap" }}
          />
        </Stack>
      </Stack>
    );
  }

  return (
    <Button
      variant="contained"
      startIcon={<CloudUpload />}
      onClick={handleInitialUpload}
      fullWidth
    >
      Upload VIPs from file
    </Button>
  );
};

export default VipUpload;
