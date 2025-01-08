export type Weapon = string

export enum WeaponType {
  Infantry = "infantry",
  Bazooka = "bazooka",
  Grenade = "grenade",
  MachineGun = "machine_gun",
  Sniper = "sniper",
  Mine = "mine",
  PAK = "pak",
  Satchel = "satchel",
  Artillery = "artillery",
  Armor = "armor",
  Commander = "commander",
}

export enum SimpleWeaponType {
  Infantry = "infantry",
  Explosive = "explosive",
  Armor = "armor",
  Commander = "commander",
  Artillery = "artillery",
  MachineGun = "machine_gun",
}

export const weaponTypeToSimpleWeaponType: Record<WeaponType, SimpleWeaponType> = {
  [WeaponType.Infantry]: SimpleWeaponType.Infantry,
  [WeaponType.Bazooka]: SimpleWeaponType.Explosive,
  [WeaponType.Grenade]: SimpleWeaponType.Explosive,
  [WeaponType.MachineGun]: SimpleWeaponType.MachineGun,
  [WeaponType.Sniper]: SimpleWeaponType.Infantry,
  [WeaponType.Mine]: SimpleWeaponType.Explosive,
  [WeaponType.PAK]: SimpleWeaponType.Explosive,
  [WeaponType.Satchel]: SimpleWeaponType.Explosive,
  [WeaponType.Artillery]: SimpleWeaponType.Artillery,
  [WeaponType.Armor]: SimpleWeaponType.Armor,
  [WeaponType.Commander]: SimpleWeaponType.Commander,
}
