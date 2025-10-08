import { getMaxValue, getMinValue } from "./index2";

export const useInputHandlers = (pendingSettings, setPendingSettings) => {
  const handleInputChange = (key) => (event) => {
    const type = event.target.type;
    const value =
      type === "number"
        ? event.target.value === ""
          ? ""
          : Number(event.target.value)
        : event.target.value;
    setPendingSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleBlur = (key) => () => {
    if (pendingSettings[key] < 0) {
      setPendingSettings((prev) => ({ ...prev, [key]: getMinValue(key) }));
    } else if (pendingSettings[key] > getMaxValue(key)) {
      setPendingSettings((prev) => ({ ...prev, [key]: getMaxValue(key) }));
    }
  };

  const handleToggleChange = (key) => (checked) => {
    setPendingSettings((prev) => ({ ...prev, [key]: checked }));
  };

  const handleSliderChange = (key) => (event, value) => {
    setPendingSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleSelectChange = (key) => (event) => {
    setPendingSettings((prev) => ({
      ...prev,
      [key]: event.target.value,
    }));
  };

  return {
    handleInputChange,
    handleBlur,
    handleToggleChange,
    handleSliderChange,
    handleSelectChange,
  };
};
