import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Convierte nombres de columnas de snake_case a formato legible
 * Flujo:
 * 1. Reemplazar _ por espacio
 * 2. Convertir cada palabra a Title Case (primera mayúscula, resto minúscula)
 * 
 * Ejemplos:
 * - product_name -> product name -> Product Name
 * - average_price -> average price -> Average Price
 * - total_amount -> total amount -> Total Amount
 */
export function formatColumnName(columnName: string): string {
  if (!columnName) return columnName;
  
  // Convertir a string
  const name = String(columnName).trim();
  if (!name) return columnName;
  
  // Paso 1: Reemplazar _ por espacio
  const withSpaces = name.replace(/_/g, ' ');
  
  // Paso 2: Convertir cada palabra a Title Case
  // Separar por espacios y capitalizar cada palabra
  const formatted = withSpaces
    .split(' ')
    .filter(word => word.length > 0) // Filtrar espacios múltiples
    .map(word => {
      // Title Case: primera letra mayúscula, resto minúscula
      const firstChar = word.charAt(0).toUpperCase();
      const rest = word.slice(1).toLowerCase();
      return firstChar + rest;
    })
    .join(' ');
  
  // Debug temporal - remover después
  if (name.includes('_')) {
    console.log(`[formatColumnName] "${name}" -> "${formatted}"`);
  }
  
  return formatted;
}

/**
 * Formatea números con separadores de miles y decimales
 * Ejemplos:
 * - 1234.56 -> "1,234.56"
 * - 1234567.89 -> "1,234,567.89"
 * - 1000 -> "1,000"
 */
export function formatNumber(value: any): string {
  if (value === null || value === undefined) {
    return "—";
  }
  
  // Intentar convertir a número
  const num = typeof value === 'number' ? value : parseFloat(String(value));
  
  // Si no es un número válido, retornar el valor original como string
  if (isNaN(num)) {
    return String(value);
  }
  
  // Formatear con separadores de miles y decimales
  // Usar configuración en-US: punto para decimales, coma para miles
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 10, // Permitir hasta 10 decimales
  });
}
