export const ROLES = {
  COMMANDER: "armycommander",
  SQUAD_LEAD: "officer",
  RIFLEMAN: "rifleman",
  ENGINEER: "engineer",
  MEDIC: "medic",
  ANTI_TANK: "antitank",
  AUTOMATIC_RIFLEMAN: "automaticrifleman",
  ASSAULT: "assault",
  MACHINE_GUNNER: "heavymachinegunner",
  SUPPORT: "support",
  SPOTTER: "spotter",
  SNIPER: "sniper",
  TANK_COMMANDER: "tankcommander",
  CREWMAN: "crewman",
  ARTILLERY_OBSERVER: "artilleryobserver",
  OPERATOR: "operator",
  GUNNER: "gunner",
};

export const ROLES_TO_LABELS = {
  [ROLES.COMMANDER]: "Commander",
  [ROLES.SQUAD_LEAD]: "Squad Lead",
  [ROLES.RIFLEMAN]: "Rifleman",
  [ROLES.ENGINEER]: "Engineer",
  [ROLES.MEDIC]: "Medic",
  [ROLES.ANTI_TANK]: "Anti-Tank",
  [ROLES.AUTOMATIC_RIFLEMAN]: "Automatic Rifleman",
  [ROLES.ASSAULT]: "Assault",
  [ROLES.MACHINE_GUNNER]: "Machinegunner",
  [ROLES.SUPPORT]: "Support",
  [ROLES.SPOTTER]: "Spotter",
  [ROLES.SNIPER]: "Sniper",
  [ROLES.TANK_COMMANDER]: "Tank Commander",
  [ROLES.CREWMAN]: "Crewman",
  [ROLES.ARTILLERY_OBSERVER]: "Artillery Observer",
  [ROLES.OPERATOR]: "Operator",
  [ROLES.GUNNER]: "Gunner",
};


export const getAllRoles = () => [
  { value: ROLES.COMMANDER, label: ROLES_TO_LABELS[ROLES.COMMANDER] },
  { value: ROLES.SQUAD_LEAD, label: ROLES_TO_LABELS[ROLES.SQUAD_LEAD] },
  { value: ROLES.RIFLEMAN, label: ROLES_TO_LABELS[ROLES.RIFLEMAN] },
  { value: ROLES.ASSAULT, label: ROLES_TO_LABELS[ROLES.ASSAULT] },
  { value: ROLES.AUTOMATIC_RIFLEMAN, label: ROLES_TO_LABELS[ROLES.AUTOMATIC_RIFLEMAN] },
  { value: ROLES.MEDIC, label: ROLES_TO_LABELS[ROLES.MEDIC] },
  { value: ROLES.SUPPORT, label: ROLES_TO_LABELS[ROLES.SUPPORT] },
  { value: ROLES.MACHINE_GUNNER, label: ROLES_TO_LABELS[ROLES.MACHINE_GUNNER] },
  { value: ROLES.ANTI_TANK, label: ROLES_TO_LABELS[ROLES.ANTI_TANK] },
  { value: ROLES.ENGINEER, label: ROLES_TO_LABELS[ROLES.ENGINEER] },
  { value: ROLES.TANK_COMMANDER, label: ROLES_TO_LABELS[ROLES.TANK_COMMANDER] },
  { value: ROLES.CREWMAN, label: ROLES_TO_LABELS[ROLES.CREWMAN] },
  { value: ROLES.SPOTTER, label: ROLES_TO_LABELS[ROLES.SPOTTER] },
  { value: ROLES.SNIPER, label: ROLES_TO_LABELS[ROLES.SNIPER] },
  { value: ROLES.ARTILLERY_OBSERVER, label: ROLES_TO_LABELS[ROLES.ARTILLERY_OBSERVER] },
  { value: ROLES.OPERATOR, label: ROLES_TO_LABELS[ROLES.OPERATOR] },
  { value: ROLES.GUNNER, label: ROLES_TO_LABELS[ROLES.GUNNER] },
];

export const getRoleLabel = (roleValue) => {
  return ROLES_TO_LABELS[roleValue] || roleValue;
};

