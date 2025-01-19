import React from 'react';
import { useTranslation } from "react-i18next";
import { siObsstudio } from "simple-icons";
import { SimpleIcon } from "@/components/simple-icon";

const StreamTutorial = () => {
  const { t } = useTranslation('translation', { keyPrefix: 'streaming.tutorial' });

  const cssExample = `body, main, .stream-banner {
  background: transparent !important;
  background-color: transparent;
}`;

  const steps = [
    {
      id: 'obs',
      content: t("openOBS"),
      icon: <SimpleIcon size={20} icon={siObsstudio} className="dark:fill-current inline-block ml-2" />
    },
    {
      id: 'source',
      content: t("createSource")
    },
    {
      id: 'values',
      content: t("enterFollowingValues"),
      subContent: (
        <div className="ml-4 space-y-2 mt-2">
          <p className="flex justify-between">
            <span className="font-semibold">{t("url")}:</span>
            <span className="font-mono">{window.location.href}</span>
          </p>
          <p className="flex justify-between">
            <span className="font-semibold">{t("width")}:</span>
            <span className="font-mono">1000</span>
          </p>
          <p className="flex justify-between">
            <span className="font-semibold">{t("height")}:</span>
            <span className="font-mono">800</span>
          </p>
          <p className="font-semibold">{t("customCSS")}:</p>
          <pre
            className="w-full p-4 bg-accent rounded-md font-mono text-sm text-gray-100 whitespace-pre overflow-x-auto">
            {cssExample}
          </pre>
          <p className="italic">{t("andSave")}</p>
        </div>
      )
    },
    {
      id: 'crop',
      content: t("crop")
    },
    {
      id: 'settings',
      content: t("changeSettings")
    }
  ];

  return (
    <div className="w-full flex justify-center">
      <div className="w-96 space-y-3">
        <div className="space-y-3">
          <p>{t("introduction")}</p>
          <p>{t("stepByStep")}</p>
        </div>

        <ol className="space-y-4">
          {steps.map((step, index) => (
            <li key={step.id} className="flex flex-col">
              <div className="flex items-center">
                <span className="font-semibold">{index + 1}. </span>
                <span className="ml-2">{step.content}</span>
                {step.icon}
              </div>
              {step.subContent}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
};

export default StreamTutorial;
