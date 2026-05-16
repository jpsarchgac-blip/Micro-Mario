// Note frequency table, mirrored from music.py NOTES dict.
export const NOTES: Record<string, number> = {
  C3: 131,  C3s: 139, D3: 147,  D3s: 156, E3: 165,
  F3: 175,  F3s: 185, G3: 196,  G3s: 208, A3: 220, A3s: 233, B3: 247,
  C4: 262,  C4s: 277, D4: 294,  D4s: 311, E4: 330,
  F4: 349,  F4s: 370, G4: 392,  G4s: 415, A4: 440, A4s: 466, B4: 494,
  C5: 523,  C5s: 554, D5: 587,  D5s: 622, E5: 659,
  F5: 698,  F5s: 740, G5: 784,  G5s: 831, A5: 880, A5s: 932, B5: 988,
  C6: 1047, D6: 1175, E6: 1319, F6: 1397, G6: 1568,
  "-": 0,
};

export const NOTE_NAMES = Object.keys(NOTES);

// Sorted list (lowest -> highest) for sequencer rows
export const NOTE_ROWS: string[] = [
  ...NOTE_NAMES.filter((n) => n !== "-").sort((a, b) => NOTES[a] - NOTES[b]),
  "-",
];

export function freqOf(pitch: string | number): number {
  if (typeof pitch === "number") return pitch;
  return NOTES[pitch] ?? 0;
}
