export type EjeCoordenada = 'lat' | 'lng';

const DMS_RE =
  /^\s*([+-])?\s*(\d+(?:[.,]\d+)?)\s*(?:°|º|d)?\s*(?:(\d+(?:[.,]\d+)?)\s*(?:'|´|′|m)?\s*)?(?:(\d+(?:[.,]\d+)?)\s*(?:"|″|′′|''|´´|s)?\s*)?([NSEWnsew])?\s*$/;

const PREFIJO_HEM_RE = /^([NSEWnsew])\s*(.+)$/;

/**
 * Interpreta una coordenada en grados decimales o notación DMS.
 * Acepta 25.25, -109.5, 25°15'30"N, 25º 15´, N 25°15', 109°00'W.
 * Devuelve grados decimales o null si el texto no es válido.
 */
export function parseCoordinate(
  valor: string | number | null | undefined,
  eje: EjeCoordenada,
): number | null {
  if (valor === null || valor === undefined) return null;

  let texto = String(valor).trim();
  if (!texto) return null;

  let hemPrefijo: string | null = null;
  const prefijo = texto.match(PREFIJO_HEM_RE);
  if (prefijo) {
    hemPrefijo = prefijo[1];
    texto = prefijo[2];
  }

  const match = texto.match(DMS_RE);
  if (!match) return null;

  const numero = (grupo?: string) => (grupo ? Number(grupo.replace(',', '.')) : 0);
  const grados = numero(match[2]);
  const minutos = numero(match[3]);
  const segundos = numero(match[4]);

  if (!Number.isFinite(grados) || minutos >= 60 || segundos >= 60) return null;

  let decimal = grados + minutos / 60 + segundos / 3600;

  if (match[1] === '-') {
    decimal = -decimal;
  }

  const hemisferio = (match[5] || hemPrefijo || '').toUpperCase();
  if (hemisferio) {
    decimal = Math.abs(decimal) * (hemisferio === 'S' || hemisferio === 'W' ? -1 : 1);
  } else if (!match[1] && eje === 'lng' && decimal > 0) {
    // Convención para México: las longitudes al oeste son negativas.
    decimal = -decimal;
  }

  const limite = eje === 'lng' ? 180 : 90;
  return decimal >= -limite && decimal <= limite ? decimal : null;
}
