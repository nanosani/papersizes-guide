export interface PaperSize {
  slug: string;
  name: string;
  series: string;
  series_name: string;
  std: string;
  aliases: string[];
  url: string;
  cat: string;
  region: string;
  widthMm: number;
  heightMm: number;
  widthCm: number;
  heightCm: number;
  widthIn: number;
  heightIn: number;
  widthPt: number;
  heightPt: number;
  ratio: number;
  ratioLabel: string;
  areaMm2: number;
  areaM2: number;
  diagonalMm: number;
  orientation: 'portrait' | 'landscape';
  /** Pixel dimensions [width, height] at the given resolution. */
  pixels(dpi: number): [number, number];
  /** Weight of one sheet in grams at the given gsm. */
  weight(gsm: number): number;
}

export interface Series {
  slug: string;
  name: string;
  standard: string;
  url: string;
}

export interface Match {
  size: PaperSize;
  diffMm: number;
  rotated: boolean;
}

export interface FindOptions {
  unit?: 'mm' | 'cm' | 'in' | 'pt';
  limit?: number;
}

export function all(): PaperSize[];
export function get(nameOrSlug: string): PaperSize | null;
export function find(width: number, height: number, options?: FindOptions): Match[];
export function series(slug: string): PaperSize[];
export function seriesList(): Series[];

export const version: string;
export const licence: string;
export const attribution: string;
export const source: string;
