# Conjunto de Preguntas para Probar el Chatbot NL → SQL

## 🆕 Preguntas con JOINs a Tablas de Dimensiones

El sistema soporta un modelo de estrella (star schema) con las siguientes relaciones:
- `contracts_gold_2.product_id → DimProducts.product_id`
- `contracts_gold_2.province_id → DimProvince.province_id`
- `contracts_gold_2.agreement_date → DimTime.date_id`

**Dataset de dimensiones**: `Dim` (separado del dataset `Gold` donde está la fact table)

### Ejemplos de Preguntas con JOINs:

- **"List contracts grouped by province name"**
  - Requiere JOIN con DimProvince para obtener nombres de provincias
  - SQL esperado: JOIN entre contracts_gold_2 y DimProvince

- **"Show me contracts with product names"**
  - Requiere JOIN con DimProducts para obtener nombres de productos
  - SQL esperado: JOIN entre contracts_gold_2 y DimProducts

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

## 📊 20+ Preguntas que GENERAN GRÁFICOS

Estas preguntas retornan datos que el LLM recomendará visualizar con gráficos:

### 1. Distribuciones y Conteos con JOINs (Pie Chart / Bar Chart)

- **"How many contracts are there by province name?"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProvince
  - Agrupa por nombre de provincia y cuenta

- **"Show me the distribution of contracts by product name"**
  - Tipo esperado: Pie Chart o Bar Chart
  - Requiere JOIN con DimProducts
  - Agrupa por nombre de producto y cuenta

- **"What is the count of contracts by product category?"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProducts
  - Agrupa por categoría de producto y cuenta

- **"List contracts grouped by province name"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProvince
  - Agrupa por nombre de provincia

- **"Show me contracts by product type"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProducts
  - Agrupa por tipo de producto

### 2. Agregaciones Numéricas por Categoría con JOINs (Bar Chart)

- **"What is the total quantity by product name?"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProducts
  - Agrupa por nombre de producto y suma CANTIDAD

- **"Show me the average price per product name"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProducts
  - Agrupa por nombre de producto y calcula promedio de PRECIO

- **"What is the total contract value by province name?"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProvince
  - Agrupa por nombre de provincia y suma valores

- **"Show me the total quantity delivered by province name"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProvince
  - Agrupa por nombre de provincia y suma CANTIDAD entregada

- **"What is the total value by product category?"**
  - Tipo esperado: Bar Chart
  - Requiere JOIN con DimProducts
  - Agrupa por categoría de producto y suma valores

- **"Show me contracts grouped by province and product name"**
  - Tipo esperado: Bar Chart (agrupado)
  - Requiere JOINs con DimProvince y DimProducts
  - Agrupa por provincia y producto

### 3. Series Temporales con JOINs (Line Chart)

- **"Show me the number of contracts per month in 2025"**
  - Tipo esperado: Line Chart
  - Requiere JOIN con DimTime
  - Agrupa por mes y cuenta

- **"What is the total quantity contracted over time by month?"**
  - Tipo esperado: Line Chart o Area Chart
  - Requiere JOIN con DimTime
  - Agrupa por mes y suma CANTIDAD

- **"Show me contracts by year and month"**
  - Tipo esperado: Line Chart
  - Requiere JOIN con DimTime
  - Agrupa por año y mes

- **"What is the trend of contract values over time by quarter?"**
  - Tipo esperado: Line Chart
  - Requiere JOIN con DimTime
  - Agrupa por trimestre y suma valores

- **"Show me contracts grouped by month name"**
  - Tipo esperado: Line Chart
  - Requiere JOIN con DimTime
  - Agrupa por nombre del mes

### 4. Preguntas Simples sin JOINs (que también generan gráficos)

- **"How many contracts are there by status?"**
  - Tipo esperado: Pie Chart o Bar Chart
  - No requiere JOIN
  - Agrupa por ESTADOCONTRATO y cuenta

- **"How many contracts are there by currency type?"**
  - Tipo esperado: Pie Chart
  - No requiere JOIN
  - Agrupa por MONEDA y cuenta

---

## 📋 15+ Preguntas que NO GENERAN GRÁFICOS

Estas preguntas retornan datos que no son adecuados para visualización (demasiadas filas, datos detallados, etc.):

### 1. Consultas de Detalle con JOINs (Listas)

- **"Show me the last 10 contracts with product names"**
  - Retorna: Lista detallada de contratos con nombres de productos
  - Requiere JOIN con DimProducts
  - No gráfico: Demasiadas columnas, datos individuales

- **"List all contracts for SOYBEAN in 2025 with province names"**
  - Retorna: Lista completa de contratos de soja con nombres de provincias
  - Requiere JOINs con DimProducts y DimProvince
  - No gráfico: Datos detallados, no agregados

- **"Show me contracts with full product and province information"**
  - Retorna: Lista detallada con información de dimensiones
  - Requiere JOINs con DimProducts y DimProvince
  - No gráfico: Demasiadas columnas, datos individuales

- **"List contracts with product names and provinces"**
  - Retorna: Lista detallada con JOINs a dimensiones
  - Requiere JOINs con DimProducts y DimProvince
  - No gráfico: Datos individuales, no agregados

- **"Show me contracts with date information by month and year"**
  - Retorna: Lista detallada con información temporal estructurada
  - Requiere JOIN con DimTime
  - No gráfico: Datos individuales

### 2. Consultas de Detalle sin JOINs (Listas)

- **"Show me the last 10 contracts"**
  - Retorna: Lista detallada de contratos
  - No gráfico: Demasiadas columnas, datos individuales

- **"Show me contracts with status TERMINADO"**
  - Retorna: Lista de contratos terminados
  - No gráfico: Datos individuales, no resumen

- **"What are the contracts for client NVD PARTICIPACIONES S.A.?"**
  - Retorna: Lista de contratos de un cliente específico
  - No gráfico: Datos detallados por contrato

### 3. Consultas de Un Solo Valor (Escalares)

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

### 4. Consultas con Muchas Filas (Tablas Grandes)

- **"Show me all contracts from 2024"**
  - Retorna: Muchas filas (probablemente >100)
  - Puede usar JOIN con DimTime para filtrar por fecha
  - No gráfico: Demasiados datos para visualizar

- **"List all contracts ordered by date"**
  - Retorna: Lista completa ordenada
  - Puede usar JOIN con DimTime para mejor ordenamiento
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

## 🔗 Notas sobre JOINs con Tablas de Dimensiones

El sistema ahora puede generar SQL con JOINs automáticos cuando:

- **Se mencionan nombres o descripciones de productos**: El LLM detectará que necesita JOIN con `DimProducts`
- **Se mencionan nombres de provincias o ubicaciones**: El LLM detectará que necesita JOIN con `DimProvince`
- **Se hacen consultas temporales estructuradas**: El LLM puede usar JOIN con `DimTime` para mejor granularidad
- **Se agrupa por categorías de dimensiones**: El LLM generará JOINs apropiados para obtener información descriptiva

**Ejemplos de detección automática**:
- "province name" o "nombre de provincia" → JOIN con DimProvince
- "product name" o "nombre de producto" → JOIN con DimProducts
- "by month" o "by year" → Puede usar JOIN con DimTime
- "product category" → JOIN con DimProducts (si tiene categorías)

**Dataset de dimensiones**: Las tablas de dimensiones están en el dataset `Dim`, separado del dataset `Gold` donde está la fact table `contracts_gold_2`.

---

## 🎯 Cómo Usar Este Conjunto

1. **Prueba las preguntas con JOINs** para verificar que el LLM genera correctamente los JOINs con las tablas de dimensiones
2. **Prueba las preguntas con gráficos** para verificar que el LLM recomienda correctamente el tipo de visualización
3. **Prueba las preguntas sin gráficos** para verificar que el sistema no intenta visualizar datos inadecuados
4. **Observa los logs** para ver cómo el LLM analiza los datos y toma decisiones
5. **Verifica la calidad de los gráficos** generados y ajusta si es necesario
6. **Revisa los SQL generados** para confirmar que los JOINs son correctos y eficientes

## 📝 Estructura del Modelo de Datos

### Fact Table
- **`contracts_gold_2`** (en dataset `Gold`): Tabla principal con hechos de contratos
  - `product_id` → Relación con DimProducts
  - `province_id` → Relación con DimProvince
  - `agreement_date` → Relación con DimTime

### Dimension Tables (en dataset `Dim`)
- **`DimProducts`**: Información de productos
  - `product_id` (PK)
  - Columnas adicionales según schema (nombre, categoría, tipo, etc.)

- **`DimProvince`**: Información de provincias
  - `province_id` (PK)
  - Columnas adicionales según schema (nombre, región, código, etc.)

- **`DimTime`**: Información temporal estructurada
  - `date_id` (PK)
  - Columnas adicionales según schema (año, mes, trimestre, día de la semana, etc.)

---

## 🧪 Preguntas de Prueba Recomendadas

### Para Probar JOINs Básicos:
1. "List contracts grouped by province name"
2. "Show me contracts with product names"
3. "Total quantity by product name"

### Para Probar JOINs Múltiples:
1. "Contracts grouped by province and product name"
2. "Show me contracts with product and province information"
3. "Total value by province and product category"

### Para Probar JOINs Temporales:
1. "Contracts grouped by month and year"
2. "Total quantity by quarter"
3. "Contracts by month name"

### Para Probar Agregaciones con JOINs:
1. "Average price by product name"
2. "Total contracts by province name"
3. "Sum of quantities by product category"

### Para Verificar que NO Hace JOINs Innecesarios:
1. "How many contracts are there?" (no necesita JOIN)
2. "Show me the last 10 contracts" (no necesita JOIN)
3. "Contracts by status" (no necesita JOIN, status está en fact table)

---

## 📚 Ejemplos de SQL Esperados

### Con JOIN Simple:
```sql
SELECT 
    DimProvince.province_name,
    COUNT(*) as total_contracts
FROM `bunge-de-poc-insumos.Gold.contracts_gold_2` c
JOIN `bunge-de-poc-insumos.Dim.DimProvince` DimProvince 
    ON c.province_id = DimProvince.province_id
GROUP BY DimProvince.province_name
LIMIT 100
```

### Con JOIN Múltiple:
```sql
SELECT 
    DimProvince.province_name,
    DimProducts.product_name,
    SUM(c.quantity) as total_quantity
FROM `bunge-de-poc-insumos.Gold.contracts_gold_2` c
JOIN `bunge-de-poc-insumos.Dim.DimProvince` DimProvince 
    ON c.province_id = DimProvince.province_id
JOIN `bunge-de-poc-insumos.Dim.DimProducts` DimProducts 
    ON c.product_id = DimProducts.product_id
GROUP BY DimProvince.province_name, DimProducts.product_name
LIMIT 100
```

### Con JOIN Temporal:
```sql
SELECT 
    DimTime.month_name,
    DimTime.year,
    COUNT(*) as contracts_count
FROM `bunge-de-poc-insumos.Gold.contracts_gold_2` c
JOIN `bunge-de-poc-insumos.Dim.DimTime` DimTime 
    ON c.agreement_date = DimTime.date_id
GROUP BY DimTime.month_name, DimTime.year
ORDER BY DimTime.year, DimTime.month
LIMIT 100
```
