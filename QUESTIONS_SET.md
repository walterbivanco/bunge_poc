# Conjunto de Preguntas para Probar el Chatbot NL → SQL

## 📊 10 Preguntas que GENERAN GRÁFICOS

Estas preguntas retornan datos que el LLM recomendará visualizar con gráficos:

### 1. Distribuciones y Conteos (Pie Chart / Bar Chart)
- **"How many contracts are there by status?"**
  - Tipo esperado: Pie Chart o Bar Chart
  - Agrupa por ESTADOCONTRATO y cuenta

- **"Show me the distribution of contracts by product type"**
  - Tipo esperado: Pie Chart o Bar Chart
  - Agrupa por PRODUCTO y cuenta

- **"What is the count of contracts by province?"**
  - Tipo esperado: Bar Chart
  - Agrupa por PROVINCIA y cuenta

- **"How many contracts are there by currency type?"**
  - Tipo esperado: Pie Chart
  - Agrupa por MONEDA y cuenta

### 2. Agregaciones Numéricas por Categoría (Bar Chart)
- **"What is the total quantity by product?"**
  - Tipo esperado: Bar Chart
  - Agrupa por PRODUCTO y suma CANTIDAD

- **"Show me the average price per product type"**
  - Tipo esperado: Bar Chart
  - Agrupa por PRODUCTO y calcula promedio de PRECIO

- **"What is the total contract value by status?"**
  - Tipo esperado: Bar Chart
  - Agrupa por ESTADOCONTRATO y suma valores

- **"Show me the total quantity delivered by province"**
  - Tipo esperado: Bar Chart
  - Agrupa por PROVINCIA y suma CANTIDAD entregada

### 3. Series Temporales (Line Chart)
- **"Show me the number of contracts per month in 2025"**
  - Tipo esperado: Line Chart
  - Agrupa por mes de FECHACONCERTACION y cuenta

- **"What is the total quantity contracted over time by month?"**
  - Tipo esperado: Line Chart o Area Chart
  - Agrupa por mes y suma CANTIDAD

---

## 📋 10 Preguntas que NO GENERAN GRÁFICOS

Estas preguntas retornan datos que no son adecuados para visualización (demasiadas filas, datos detallados, etc.):

### 1. Consultas de Detalle (Listas)
- **"Show me the last 10 contracts"**
  - Retorna: Lista detallada de contratos
  - No gráfico: Demasiadas columnas, datos individuales

- **"List all contracts for SOYBEAN in 2025"**
  - Retorna: Lista completa de contratos de soja
  - No gráfico: Datos detallados, no agregados

- **"Show me contracts with status TERMINADO"**
  - Retorna: Lista de contratos terminados
  - No gráfico: Datos individuales, no resumen

- **"What are the contracts for client NVD PARTICIPACIONES S.A.?"**
  - Retorna: Lista de contratos de un cliente específico
  - No gráfico: Datos detallados por contrato

### 2. Consultas de Un Solo Valor (Escalares)
- **"What is the total number of contracts?"**
  - Retorna: Un solo número (COUNT)
  - No gráfico: Solo un valor, no hay comparación

- **"What is the average price of all contracts?"**
  - Retorna: Un solo valor promedio
  - No gráfico: Un solo dato numérico

- **"How many contracts are there in total?"**
  - Retorna: Un solo número
  - No gráfico: No hay distribución ni comparación

- **"What is the maximum quantity in a single contract?"**
  - Retorna: Un solo valor máximo
  - No gráfico: Un solo dato

### 3. Consultas con Muchas Filas (Tablas Grandes)
- **"Show me all contracts from 2024"**
  - Retorna: Muchas filas (probablemente >100)
  - No gráfico: Demasiados datos para visualizar

- **"List all contracts ordered by date"**
  - Retorna: Lista completa ordenada
  - No gráfico: Demasiadas filas, datos individuales

---

## 💡 Notas sobre la Generación de Gráficos

El sistema utiliza **Gemini (LLM)** para determinar si los datos deben visualizarse:

- **Genera gráficos cuando**:
  - Hay datos agregados (GROUP BY)
  - Hay comparaciones entre categorías
  - Hay series temporales
  - El número de filas es razonable (≤100)
  - Hay una relación clara entre categorías y valores numéricos

- **NO genera gráficos cuando**:
  - Solo hay un valor (escalar)
  - Hay demasiadas filas (>100)
  - Los datos son muy detallados (no agregados)
  - No hay una estructura clara para visualizar

## 🎯 Cómo Usar Este Conjunto

1. **Prueba las preguntas con gráficos** para verificar que el LLM recomienda correctamente el tipo de visualización
2. **Prueba las preguntas sin gráficos** para verificar que el sistema no intenta visualizar datos inadecuados
3. **Observa los logs** para ver cómo el LLM analiza los datos y toma decisiones
4. **Verifica la calidad de los gráficos** generados y ajusta si es necesario
