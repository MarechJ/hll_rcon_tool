import { gameSwitch } from "@/utils/lib";
import HLLMapObjectivesPage from "./hll";
import HLLVMapObjectivesPage from "./hllv";

function MapObjectivesPage() {
    return gameSwitch(<HLLMapObjectivesPage />, <HLLVMapObjectivesPage />)
}

export default MapObjectivesPage;