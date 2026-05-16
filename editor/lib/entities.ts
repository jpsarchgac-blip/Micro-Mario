// Entity type strings, mirrored from entity.py / entity_new.py / make_entity_new
export const ENTITY_TYPES = [
  { id: "goomba",       label: "GOOMBA",        category: "enemy",  color: "#a16207" },
  { id: "bat",          label: "BAT",           category: "enemy",  color: "#5b21b6" },
  { id: "fish",         label: "FISH",          category: "enemy",  color: "#0ea5e9" },
  { id: "pata_new",     label: "PATAPATA",      category: "enemy",  color: "#16a34a" },
  { id: "killer_spawn", label: "KILLER SPAWN",  category: "enemy",  color: "#ef4444" },
  { id: "boss",         label: "BOSS",          category: "enemy",  color: "#dc2626" },
  { id: "big_mushroom", label: "TRAMPOLINE",    category: "gimmick", color: "#f472b6" },
  { id: "qblock_random", label: "Q-SLOT",       category: "gimmick", color: "#facc15" },
] as const;

export type EntityType = (typeof ENTITY_TYPES)[number]["id"];

export function entityColor(id: string): string {
  return ENTITY_TYPES.find((e) => e.id === id)?.color ?? "#888";
}

export function entityLabel(id: string): string {
  return ENTITY_TYPES.find((e) => e.id === id)?.label ?? id.toUpperCase();
}
