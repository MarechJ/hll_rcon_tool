import React, { useEffect, useMemo, useState } from "react";
import { Await, defer, Link, useLoaderData, useSubmit } from "react-router-dom";
import { cmd } from "@/utils/fetchUtils";
import { ErrorSection } from "@/components/shared/ErrorSection";
import {
  Autocomplete,
  Box,
  Button,
  Paper,
  Skeleton,
  Stack,
  TextField,
} from "@mui/material";
import "@fontsource/montserrat";
import AddCommentIcon from "@mui/icons-material/AddComment";
import { TEMPLATE_CATEGORY, unpackBroadcastMessage } from "@/utils/lib";
import { BroadcastFields } from "@/components/shared/BroadcastFields";
import Padlock from "@/components/shared/Padlock";
import isMatch from "lodash/isMatch";
import isEqual from "lodash/eq";

export const loader = async () => {
  const config = await cmd.GET_BROADCAST_CONFIG();
  const templates = cmd.GET_MESSAGE_TEMPLATES({
    params: { category: TEMPLATE_CATEGORY.BROADCAST },
  });
  return defer({ config, templates });
};

export const action = async ({ request }) => {
  const payload = await request.json();
  const result = await cmd.SET_BROADCAST_CONFIG({ payload });
  return result;
};

const TemplateSkeleton = () => <Skeleton height={80} />;

const BroadcastMessagePage = () => {
  const data = useLoaderData();
  const submit = useSubmit();
  const [config, setConfig] = useState(data.config);
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(false);
    setConfig(data.config);
  }, [data.config]);

  const handleApplyClick = (e) => {
    setLoading(true);
    const payload = {
      messages: config.messages,
      randomize: config.randomize,
      enabled: config.enabled,
    };
    submit(payload, { method: "post", encType: "application/json" });
  };

  const handleTemplateChange = (e, message) => {
    setConfig((prev) => ({
      ...prev,
      messages: message ? unpackBroadcastMessage(message.content) : data.config.messages,
    }));
  };

  const handleMessagesChange = (messages) => {
    setConfig((prev) => ({
      ...prev,
      messages,
    }));
  };

  const hasChanges = useMemo(
    () =>
      // the config is not the same
      !isMatch(config, data.config) ||
      // OR the messages have diff length
      config.messages.length !== data.config.messages.length ||
      // OR some messages are not the same
      config.messages.some(
        (message, index) => !isEqual(message, data.config.messages[index])
      ),
    [config, data.config]
  );

  const validMessages = useMemo(
    () =>
      config.messages.every(
        (message) =>
          // it has both fields, time_sec not negative and message is not only empty chars
          message.time_sec && message.time_sec > 0 && message.message.trim()
      ),
    [config.messages]
  );

  const applyDisabled = loading || !hasChanges || !validMessages;

  return (
    <Box sx={{ maxWidth: (theme) => theme.breakpoints.values.md }}>
      <Stack
        component={Paper}
        sx={{ p: 1, mb: 1 }}
        direction={"row"}
        justifyContent={"space-between"}
        gap={1}
      >
        <Stack direction={"row"} alignItems={"center"} gap={1}>
          <Padlock
            label={config.enabled ? "Enabled" : "Disabled"}
            checked={config.enabled}
            handleChange={(checked) =>
              setConfig((prev) => ({ ...prev, enabled: checked }))
            }
          />
          <Padlock
            label={config.randomize ? "Random ON" : "Random OFF"}
            checked={config.randomize}
            handleChange={(checked) =>
              setConfig((prev) => ({ ...prev, randomize: checked }))
            }
          />
        </Stack>
        <Stack direction={"row"} alignItems={"center"} gap={1}>
          <Button
            component={Link}
            startIcon={<AddCommentIcon />}
            variant="contained"
            to={
              "/settings/templates/" + TEMPLATE_CATEGORY.BROADCAST.toLowerCase()
            }
          >
            Create Template
          </Button>
          <Button variant={"contained"} disabled={applyDisabled} onClick={handleApplyClick}>
            {loading ? "Loading..." : "Apply"} 
          </Button>
        </Stack>
      </Stack>
      <BroadcastFields
        messages={config.messages}
        onChange={handleMessagesChange}
        sx={{ mb: 2 }}
      />
      <React.Suspense fallback={<TemplateSkeleton />}>
        <Await
          resolve={data.templates}
          errorElement={<ErrorSection title={"Welcome Templates"} />}
        >
          {(templates) => {
            return (
              <Autocomplete
                id="template-select"
                fullWidth
                options={templates}
                onChange={handleTemplateChange}
                autoHighlight
                getOptionLabel={(option) => option.title}
                renderOption={(props, option) => {
                  const { key, ...optionProps } = props;
                  return (
                    <Box key={key} component="li" {...optionProps}>
                      #{option.id} {option.title}
                    </Box>
                  );
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Choose a template"
                    slotProps={{
                      htmlInput: {
                        ...params.inputProps,
                      },
                    }}
                  />
                )}
              />
            );
          }}
        </Await>
      </React.Suspense>
    </Box>
  );
};

export default BroadcastMessagePage;
