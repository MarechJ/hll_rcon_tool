import { useMutation, useQuery } from "@tanstack/react-query";
import { useLoaderData } from "react-router-dom";
import { mapsManagerMutationOptions, mapsManagerQueryKeys, mapsManagerQueryOptions } from "../../queries";
import { useEffect, useRef, useState } from "react";
import _ from "lodash";
import { toast } from "react-toastify";
import { VotemapChangeNotification } from "./VotemapChangeNotification";

function VotemapSettingsPage() {
  const loaderData = useLoaderData();

  const { data: config } = useQuery({
    ...mapsManagerQueryOptions.voteMapConfig(),
    initialData: loaderData.config,
    refetchInterval: 5_000,
    staleTime: 5_000,
    refetchOnMount: false,
  });

  const { mutate: changeConfig, isPending: isConfigChanging } = useMutation({
    ...mapsManagerMutationOptions.setVotemapConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.voteMapConfig,
      });
      toast.success(`Votemap config has been changed`);
    },
    onError: (error) => {
      toast.error(
        <div>
          <span>{error.name}</span>
          <p>{error.message}</p>
        </div>
      );
    },
  });

  const prevConfig = useRef(config);
  const [workingConfig, setWorkingConfig] = useState(config);

  // Compare incoming config changes
  const handleIncomingConfigChange = () => {
    // check how the configs differ
    const diff = _.transform(
      prevConfig.current,
      (result, value, key) => {
        if (!_.isEqual(value, config[key])) {
          result.push(key);
        }
      },
      []
    );

    // no changes do nothing
    const numberOfChanges = diff.length;
    if (numberOfChanges === 0) return;

    const enabledOnly = numberOfChanges && "enabled" in diff;
    // if only 'enabled' changed do nothing
    if (enabledOnly) return;

    console.log("CONFIG CHANGES OCCURED")

    // update reference
    // this will also prevent infinite toasting for the same changes
    prevConfig.current = config;

    // announce there have been some changes made
    toast.info(VotemapChangeNotification, {
      onClose: (changesAccepted) => {
        if (changesAccepted) {
          // only override what has actually changed on the server
          // to keep any other local changes
          setWorkingConfig((prev) => {
            const combined = { ...prev };
            diff.forEach((key) => {
              combined[key] = config[key];
            });
            return combined;
          });
        }
      },
      data: { changes: diff },
    });
  };

  const handleConfigSave = () => {
    changeConfig(workingConfig)
  }

  useEffect(handleIncomingConfigChange, [config, workingConfig]);
}

export default VotemapSettingsPage;
