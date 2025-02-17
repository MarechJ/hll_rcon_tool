export const SEEDING_MESSAGES = {
  ATTACK_4TH_CAP: (count) => 
    `You violated seeding rules on this server: Attacking 4th cap while seeding is not allowed.\nYou're being punished by a bot (${count}/-1).\nNext check in 30 seconds`,
  NO_LEADER: (squadName) =>
    `Your squad (${squadName}) must have an officer.\nYou're being punished by a bot (1/2).\nNext check in 40 seconds`
};

export const ADMIN_MESSAGES = [
  "Join our Discord @ example.com",
  "Warning: Watch your language",
  "Please follow server rules",
  "Team killing is not allowed",
  "squads without squadleaders will be kicked!!"
];

export const PUNISHMENT_REASONS = [
  "Team killing",
  "Toxic behavior",
  "Breaking seeding rules",
  "Inappropriate language"
]; 