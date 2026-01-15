# Conjunto de Preguntas para Probar el Chatbot NL → SQL

## 🆕 Preguntas con JOINs a Tablas de Dimensiones

El sistema ahora soporta un modelo de estrella (star schema) con las siguientes relaciones:
- `contracts_gold_2.product_id → DimProducts.product_id`
- `contracts_gold_2.province_id → DimProvince.province_id`
- `contracts_gold_2.agreement_date → DimTime.date_id`

### Ejemplos de Preguntas con JOINs:

- **"Show me contracts with product names"**
  - Requiere JOIN con DimProducts para obtener nombres de productos
  - SQL esperado: JOIN entre contracts_gold_2 y DimProducts

- **"List contracts grouped by province name"**
  - Requiere JOIN con DimProvince para obtener nombres de provincias
  - SQL esperado: JOIN y GROUP BY con nombre de provincia

- **"Show me contracts by product category"**
  - Requiere JOIN con DimProducts si tiene categorías
  - SQL esperado: JOIN para obtener información de categoría

- **"What are the contracts by month and year?"**
  - Requiere JOIN con DimTime para obtener información temporal estructurada
  - SQL esperado: JOIN con DimTime para agrupar por mes/año

- **"Show me product names with their total quantities"**
  - Requiere JOIN con DimProducts y agregación
  - SQL esperado: JOIN + GROUP BY + SUM

---

## 📊 15+ Preguntas que GENERAN GRÁFICOS

Estas preguntas retornan datos que el LLM recomendará visualizar con gráficos:

### 1. Distribuciones y Conteos (Pie Chart / Bar Chart)
- **"How many contracts are there by status?"**
  - Tipo esperado: Pie Chart o Bar Chart
  - Agrupa por ESTADOCONTRATO y cuenta

- **"Show me the distribution of contracts by product type"**
  - Tipo esperado: Pie Chart o Bar Chart
  - Agrupa por PRODUCTO y cuenta
  - 💡 Puede usar JOIN con DimProducts si se necesita nombre del producto

- **"What is the count of contracts by province?"**
  - Tipo esperado: Bar Chart
  - Agrupa por PROVINCIA y cuenta
  - 💡 Puede usar JOIN con DimProvince para obtener nombres de provincias

- **"How many contracts are there by currency type?"**
  - Tipo esperado: Pie Chart
  - Agrupa por MONEDA y cuenta

- **"Show me contracts grouped by product name"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProducts
  - Agrupa por nombre de producto y cuenta

### 2. Agregaciones Numéricas por Categoría (Bar Chart)
- **"What is the total quantity by product?"**
  - Tipo esperado: Bar Chart
  - Agrupa por PRODUCTO y suma CANTIDAD
  - 💡 Puede usar JOIN con DimProducts para mostrar nombres

- **"Show me the average price per product type"**
  - Tipo esperado: Bar Chart
  - Agrupa por PRODUCTO y calcula promedio de PRECIO
  - 💡 Puede usar JOIN con DimProducts

- **"What is the total contract value by status?"**
  - Tipo esperado: Bar Chart
  - Agrupa por ESTADOCONTRATO y suma valores

- **"Show me the total quantity delivered by province"**
  - Tipo esperado: Bar Chart
  - Agrupa por PROVINCIA y suma CANTIDAD entregada
  - 💡 Puede usar JOIN con DimProvince para nombres

- **"What is the total value by product name?"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProducts
  - Agrupa por nombre de producto y suma valores

### 3. Series Temporales (Line Chart)
- **"Show me the number of contracts per month in 2025"**
  - Tipo esperado: Line Chart
  - Agrupa por mes de FECHACONCERTACION y cuenta
  - 💡 Puede usar JOIN con DimTime para mejor estructura temporal

- **"What is the total quantity contracted over time by month?"**
  - Tipo esperado: Line Chart o Area Chart
  - Agrupa por mes y suma CANTIDAD
  - 💡 Puede usar JOIN con DimTime

- **"Show me contracts by year and month"**
  - Tipo esperado: Line Chart
  - Requiere JOIN con DimTime
  - Agrupa por año y mes

- **"What is the trend of contract values over time?"**
  - Tipo esperado: Line Chart
  - Agrupa por fecha y suma valores
  - 💡 Puede usar JOIN con DimTime para mejor granularidad temporal

---

## 📋 15+ Preguntas que NO GENERAN GRÁFICOS

Estas preguntas retornan datos que no son adecuados para visualización (demasiadas filas, datos detallados, etc.):

### 1. Consultas de Detalle (Listas)
- **"Show me the last 10 contracts"**
  - Retorna: Lista detallada de contratos
  - No gráfico: Demasiadas columnas, datos individuales
  - 💡 Puede incluir JOINs con dimensiones para mostrar nombres

- **"List all contracts for SOYBEAN in 2025"**
  - Retorna: Lista completa de contratos de soja
  - No gráfico: Datos detallados, no agregados
  - 💡 Puede usar JOIN con DimProducts para filtrar por nombre

- **"Show me contracts with status TERMINADO"**
  - Retorna: Lista de contratos terminados
  - No gráfico: Datos individuales, no resumen

- **"What are the contracts for client NVD PARTICIPACIONES S.A.?"**
  - Retorna: Lista de contratos de un cliente específico
  - No gráfico: Datos detallados por contrato

- **"Show me contracts with product names and provinces"**
  - Retorna: Lista detallada con información de dimensiones
  - Requiere JOINs con DimProducts y DimProvince
  - No gráfico: Datos individuales, no agregados

- **"List contracts with full product and province information"**
  - Retorna: Lista detallada con JOINs a dimensiones
  - No gráfico: Demasiadas columnas, datos individuales

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

- **"How many different products are there?"**
  - Retorna: Un solo número
  - Puede requerir JOIN con DimProducts o DISTINCT
  - No gráfico: Un solo valor

### 3. Consultas con Muchas Filas (Tablas Grandes)
- **"Show me all contracts from 2024"**
  - Retorna: Muchas filas (probablemente >100)
  - No gráfico: Demasiados datos para visualizar
  - 💡 Puede usar JOIN con DimTime para filtrar por fecha

- **"List all contracts ordered by date"**
  - Retorna: Lista completa ordenada
  - No gráfico: Demasiadas filas, datos individuales
  - 💡 Puede usar JOIN con DimTime para mejor ordenamiento

- **"Show me all contracts with product details"**
  - Retorna: Muchas filas con información de dimensiones
  - Requiere JOINs con DimProducts
  - No gráfico: Demasiados datos detallados

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

## 🔗 Notas sobre JOINs con Tablas de Dimensiones

El sistema ahora puede generar SQL con JOINs automáticos cuando:

- **Se mencionan nombres o descripciones de productos**: El LLM detectará que necesita JOIN con `DimProducts`
- **Se mencionan nombres de provincias o ubicaciones**: El LLM detectará que necesita JOIN con `DimProvince`
- **Se hacen consultas temporales estructuradas**: El LLM puede usar JOIN con `DimTime` para mejor granularidad
- **Se agrupa por categorías de dimensiones**: El LLM generará JOINs apropiados para obtener información descriptiva

**Ejemplos de detección automática**:
- "product names" → JOIN con DimProducts
- "province names" → JOIN con DimProvince
- "by month" o "by year" → Puede usar JOIN con DimTime
- "product categories" → JOIN con DimProducts (si tiene categorías)

## 🎯 Cómo Usar Este Conjunto

1. **Prueba las preguntas con JOINs** para verificar que el LLM genera correctamente los JOINs con las tablas de dimensiones
2. **Prueba las preguntas con gráficos** para verificar que el LLM recomienda correctamente el tipo de visualización
3. **Prueba las preguntas sin gráficos** para verificar que el sistema no intenta visualizar datos inadecuados
4. **Observa los logs** para ver cómo el LLM analiza los datos y toma decisiones
5. **Verifica la calidad de los gráficos** generados y ajusta si es necesario
6. **Revisa los SQL generados** para confirmar que los JOINs son correctos y eficientes

## 📝 Estructura del Modelo de Datos

### Fact Table
- **`contracts_gold_2`**: Tabla principal con hechos de contratos
  - `product_id` → Relación con DimProducts
  - `province_id` → Relación con DimProvince
  - `agreement_date` → Relación con DimTime

### Dimension Tables
- **`DimProducts`**: Información de productos
  - `product_id` (PK)
  - Columnas adicionales según schema

- **`DimProvince`**: Información de provincias
  - `province_id` (PK)
  - Columnas adicionales según schema

- **`DimTime`**: Información temporal estructurada
  - `date_id` (PK)
  - Columnas adicionales según schema (año, mes, trimestre, etc.)
