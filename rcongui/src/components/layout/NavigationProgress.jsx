import { LinearProgress } from "@mui/material";
import { useNavigation } from "react-router-dom";

const NavigationProgress = () => {
  const navigation = useNavigation();
  return (
    navigation.state === "loading" && (
      <LinearProgress
        sx={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 9999,
          height: { xs: "3px", lg: "2px" },
        }}
      />
    )
  );
};

export default NavigationProgress;
