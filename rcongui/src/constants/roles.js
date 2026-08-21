import { runtimeConfig } from "@/config/runtimeConfig";

const HLL_ROLES = [
  { value: "armycommander", label: "Commander" },
  { value: "officer", label: "Squad Lead" },
  { value: "rifleman", label: "Rifleman" },
  { value: "assault", label: "Assault" },
  { value: "automaticrifleman", label: "Automatic Rifleman" },
  { value: "medic", label: "Medic" },
  { value: "support", label: "Support" },
  { value: "heavymachinegunner", label: "Machinegunner" },
  { value: "antitank", label: "Anti-Tank" },
  { value: "engineer", label: "Engineer" },
  { value: "tankcommander", label: "Tank Commander" },
  { value: "crewman", label: "Crewman" },
  { value: "spotter", label: "Spotter" },
  { value: "sniper", label: "Sniper" },
  { value: "artilleryobserver", label: "Artillery Observer" },
  { value: "operator", label: "Operator" },
  { value: "gunner", label: "Gunner" },
];

const HLLV_ROLES = [
  { value: "armycommander", label: "Commander" },
  { value: "squadleader", label: "Squad Leader" },
  { value: "rifleman", label: "Rifleman" },
  { value: "grenadier", label: "Grenadier" },
  { value: "specialist", label: "Specialist" },
  { value: "medic", label: "Medic" },
  { value: "heavymachinegunner", label: "Machine Gunner" },
  { value: "engineer", label: "Engineer" },
  { value: "tankcommander", label: "Tank Commander" },
  { value: "crewman", label: "Crewman" },
  { value: "sniper", label: "Sniper" },
  { value: "spotter", label: "Spotter" },
  { value: "mortarobserver", label: "Mortar Observer" },
  { value: "mortargunner", label: "Mortar Gunner" },
  { value: "mortarsupport", label: "Mortar Support" },
  { value: "helicopterpilot", label: "Helicopter Pilot" },
  { value: "helicopterlogisticsofficer", label: "Helicopter Logistics Officer" },
];

const ROLES_BY_GAME = {
  hll: HLL_ROLES,
  hllv: HLLV_ROLES,
};

const LABELS_BY_GAME = Object.fromEntries(
  Object.entries(ROLES_BY_GAME).map(([game, roles]) => [
    game,
    Object.fromEntries(roles.map(({ value, label }) => [value, label])),
  ])
);

export const getAllRoles = () =>
  ROLES_BY_GAME[runtimeConfig.HLL_GAME] ?? HLL_ROLES;

export const getRoleLabel = (roleValue) =>
  (LABELS_BY_GAME[runtimeConfig.HLL_GAME] ?? LABELS_BY_GAME.hll)[roleValue] ??
  roleValue;
