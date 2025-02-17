export const SQUAD_TYPES = {
  infantry: {
    maxPlayers: 6,
    roles: [
      "officer", // squad leader
      "rifleman",
      "medic",
      "support",
      "engineer",
      "antitank",
      "assault",
      "heavymachinegunner"
    ]
  },
  armor: {
    maxPlayers: 3,
    roles: [
      "tankcommander", // squad leader
      "crewman"
    ]
  },
  recon: {
    maxPlayers: 2,
    roles: [
      "spotter", // squad leader
      "sniper"
    ]
  }
};

export const isLeaderRole = (role) => ["officer", "tankcommander", "spotter"].includes(role);

export const getSquadLeaderRole = (squadType) => ({
  infantry: "officer",
  armor: "tankcommander",
  recon: "spotter"
})[squadType];

export const getAvailableRoles = (squadType, isLeader) => {
  if (isLeader) return [getSquadLeaderRole(squadType)];
  
  return SQUAD_TYPES[squadType].roles.filter(r => {
    if (squadType === "infantry") return r !== "officer";
    if (squadType === "armor") return r === "crewman";
    if (squadType === "recon") return r === "sniper";
  });
}; 