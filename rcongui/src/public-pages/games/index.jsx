import { GamesList } from "@/pages/stats/games";
import { columns } from "./game-list-columns";
import { cmd } from "@/utils/fetchUtils";

export const loader = async () => {
  return await cmd.GET_COMPLETED_GAMES();
};

const GamesPage = () => {
  return <GamesList columns={columns} />;
};

export default GamesPage;
