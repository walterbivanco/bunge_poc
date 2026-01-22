# 📊 Modelo de Datos: Star Schema (Modelo Estrella)

## 🎯 ¿Qué es un Modelo Estrella?

Un **modelo estrella (star schema)** es una forma de organizar datos en un data warehouse que separa los **hechos** (eventos/transacciones) de las **dimensiones** (información descriptiva). Se llama "estrella" porque visualmente la tabla de hechos está en el centro y las tablas de dimensiones la rodean como los rayos de una estrella.

```
                    DimProducts
                        |
                        |
            DimProvince  |  DimTime
                 \       |       /
                  \      |      /
                   \     |     /
                    \    |    /
                     \   |   /
                  contracts_gold_2
                  (Fact Table)
```

---

## 📋 Tipos de Tablas

### 1. **Fact Table (Tabla de Hechos)** - `contracts_gold_2`

**¿Qué es?**
- Es la tabla **central** que contiene los **eventos o transacciones** que queremos analizar
- Contiene los **hechos medibles** (cantidades, precios, valores)
- Tiene **muchas filas** (puede tener millones de registros)
- Contiene **claves foráneas** que apuntan a las tablas de dimensiones

**Características:**
- ✅ Contiene medidas numéricas (cantidad, precio, valor)
- ✅ Contiene claves foráneas (product_id, province_id, agreement_date)
- ✅ Se actualiza frecuentemente (nuevos contratos se agregan constantemente)
- ✅ Tiene muchas filas pero relativamente pocas columnas

**Ejemplo de datos:**
```
contract_id | product_id | province_id | agreement_date | quantity | price | status
------------|------------|-------------|----------------|----------|-------|--------
1001        | 5          | 12          | 2025-01-15     | 1000     | 250   | ACTIVE
1002        | 3          | 8           | 2025-01-16     | 500      | 180   | ACTIVE
1003        | 5          | 12          | 2025-01-17     | 2000     | 260   | TERMINATED
```

**¿Por qué usar IDs en lugar de nombres?**
- **Ahorro de espacio**: Los IDs son pequeños (números) vs nombres largos (texto)
- **Consistencia**: Un producto siempre tiene el mismo ID, pero su nombre podría cambiar
- **Normalización**: Evita duplicar información descriptiva en cada fila
- **Rendimiento**: Los JOINs con números son más rápidos que con texto

---

### 2. **Dimension Tables (Tablas de Dimensiones)**

Las tablas de dimensiones contienen **información descriptiva** que nos ayuda a entender y categorizar los hechos. Son tablas **pequeñas** (relativamente pocas filas) pero con **muchas columnas** descriptivas.

#### **DimProducts** - Dimensión de Productos

**¿Qué contiene?**
- Información descriptiva sobre cada producto
- Un registro por cada producto único
- Columnas como: nombre del producto, categoría, tipo, descripción, etc.

**Relación:**
```
contracts_gold_2.product_id → DimProducts.product_id
```

**Ejemplo de datos:**
```
product_id | product_name      | category    | type    | description
-----------|-------------------|-------------|---------|------------
3          | SOJA              | Granos      | Commodity | Soja para exportación
5          | MAIZ              | Granos      | Commodity | Maíz amarillo
7          | TRIGO             | Granos      | Commodity | Trigo pan
```

**¿Por qué separarlo?**
- Si tienes 1 millón de contratos pero solo 50 productos, no necesitas repetir "SOJA" un millón de veces
- Si cambia el nombre de un producto, solo lo actualizas en un lugar
- Puedes agregar más información del producto sin modificar la fact table

**Ejemplo de uso:**
```sql
-- Sin JOIN (solo IDs):
SELECT product_id, quantity FROM contracts_gold_2
-- Resultado: product_id=5, quantity=1000 (no sabemos qué producto es)

-- Con JOIN (nombres descriptivos):
SELECT p.product_name, c.quantity 
FROM contracts_gold_2 c
JOIN DimProducts p ON c.product_id = p.product_id
-- Resultado: MAIZ, 1000 (ahora sabemos que es maíz)
```

---

#### **DimProvince** - Dimensión de Provincias

**¿Qué contiene?**
- Información sobre cada provincia/ubicación geográfica
- Un registro por cada provincia única
- Columnas como: nombre de provincia, región, código postal, coordenadas, etc.

**Relación:**
```
contracts_gold_2.province_id → DimProvince.province_id
```

**Ejemplo de datos:**
```
province_id | province_name    | region      | country | code
------------|------------------|-------------|---------|------
8           | BUENOS AIRES     | PAMPEANA    | ARG     | BA
12          | CORDOBA          | PAMPEANA    | ARG     | CB
15          | SANTA FE         | PAMPEANA    | ARG     | SF
```

**¿Por qué separarlo?**
- Si tienes 1 millón de contratos pero solo 24 provincias, no necesitas repetir "BUENOS AIRES" un millón de veces
- Puedes agregar información geográfica adicional (región, coordenadas) sin afectar la fact table
- Facilita análisis geográficos (agrupar por región, país, etc.)

**Ejemplo de uso:**
```sql
-- Agrupar contratos por nombre de provincia:
SELECT p.province_name, COUNT(*) as total_contracts
FROM contracts_gold_2 c
JOIN DimProvince p ON c.province_id = p.province_id
GROUP BY p.province_name
-- Resultado: BUENOS AIRES: 5000, CORDOBA: 3000, etc.
```

---

#### **DimTime** - Dimensión Temporal

**¿Qué contiene?**
- Información estructurada sobre fechas
- Un registro por cada fecha única
- Columnas como: año, mes, trimestre, día de la semana, semana del año, etc.

**Relación:**
```
contracts_gold_2.agreement_date → DimTime.date_id
```

**Ejemplo de datos:**
```
date_id  | date       | year | month | month_name | quarter | day_of_week | week_of_year
---------|------------|------|-------|------------|--------|-------------|-------------
20250115 | 2025-01-15 | 2025 | 1     | Enero      | Q1     | Miércoles   | 3
20250116 | 2025-01-16 | 2025 | 1     | Enero      | Q1     | Jueves      | 3
20250117 | 2025-01-17 | 2025 | 1     | Enero      | Q1     | Viernes     | 3
```

**¿Por qué separarlo?**
- Facilita análisis temporales complejos sin usar funciones de fecha en cada query
- Permite agrupar por trimestre, mes, año de forma más eficiente
- Puedes agregar información temporal adicional (festivos, estaciones, etc.)
- Evita calcular año/mes/trimestre en cada consulta

**Ejemplo de uso:**
```sql
-- Agrupar contratos por trimestre (sin DimTime sería más complejo):
SELECT t.quarter, COUNT(*) as total_contracts
FROM contracts_gold_2 c
JOIN DimTime t ON c.agreement_date = t.date_id
GROUP BY t.quarter
-- Resultado: Q1: 10000, Q2: 12000, etc.

-- Con DimTime también puedes hacer:
SELECT t.month_name, t.year, SUM(c.quantity) as total_quantity
FROM contracts_gold_2 c
JOIN DimTime t ON c.agreement_date = t.date_id
GROUP BY t.month_name, t.year
ORDER BY t.year, t.month
-- Resultado: Enero 2025: 50000, Febrero 2025: 55000, etc.
```

---

## 🔗 Cómo Funcionan las Relaciones

### Relación 1: Productos
```
contracts_gold_2.product_id = DimProducts.product_id
```
- Cada contrato tiene un `product_id` que identifica el producto
- Al hacer JOIN, obtenemos el nombre y otras características del producto
- **Uso típico**: "Muéstrame contratos con nombres de productos"

### Relación 2: Provincias
```
contracts_gold_2.province_id = DimProvince.province_id
```
- Cada contrato tiene un `province_id` que identifica la provincia
- Al hacer JOIN, obtenemos el nombre y región de la provincia
- **Uso típico**: "Agrupa contratos por nombre de provincia"

### Relación 3: Tiempo
```
contracts_gold_2.agreement_date = DimTime.date_id
```
- Cada contrato tiene una fecha (`agreement_date`)
- Al hacer JOIN, obtenemos información estructurada de la fecha (año, mes, trimestre)
- **Uso típico**: "Contratos agrupados por trimestre" o "Tendencia mensual"

---

## 💡 Ventajas del Modelo Estrella

### 1. **Eficiencia de Almacenamiento**
- ❌ **Sin dimensiones**: Repetir "SOJA" 1 millón de veces = mucho espacio
- ✅ **Con dimensiones**: Guardar "SOJA" 1 vez, referenciar con ID = ahorro masivo

### 2. **Mantenimiento**
- ❌ **Sin dimensiones**: Si cambia el nombre de un producto, actualizar 1 millón de filas
- ✅ **Con dimensiones**: Actualizar 1 fila en DimProducts, todos los contratos se actualizan automáticamente

### 3. **Rendimiento de Consultas**
- Los JOINs con tablas pequeñas (dimensiones) son muy rápidos
- Las dimensiones pueden tener índices optimizados
- BigQuery puede cachear dimensiones fácilmente

### 4. **Flexibilidad de Análisis**
- Puedes agregar nuevas columnas a dimensiones sin afectar la fact table
- Facilita análisis complejos (agrupar por región, por trimestre, etc.)
- Permite hacer "drill-down" (de año → mes → día)

### 5. **Consistencia de Datos**
- Un producto siempre tiene el mismo ID
- Evita inconsistencias (ej: "SOJA" vs "Soja" vs "SOJA ")
- Facilita la limpieza y estandarización de datos

---

## 🎯 Ejemplos Prácticos

### Ejemplo 1: Consulta Simple (sin JOIN)
```sql
-- Pregunta: "¿Cuántos contratos hay?"
SELECT COUNT(*) 
FROM contracts_gold_2
-- No necesita JOIN, solo cuenta filas
```

### Ejemplo 2: Consulta con un JOIN
```sql
-- Pregunta: "Muéstrame contratos con nombres de productos"
SELECT 
    p.product_name,
    c.quantity,
    c.price
FROM contracts_gold_2 c
JOIN DimProducts p ON c.product_id = p.product_id
LIMIT 100
```

### Ejemplo 3: Consulta con múltiples JOINs
```sql
-- Pregunta: "Contratos agrupados por provincia y producto"
SELECT 
    pr.province_name,
    p.product_name,
    COUNT(*) as total_contracts,
    SUM(c.quantity) as total_quantity
FROM contracts_gold_2 c
JOIN DimProducts p ON c.product_id = p.product_id
JOIN DimProvince pr ON c.province_id = pr.province_id
GROUP BY pr.province_name, p.product_name
ORDER BY total_contracts DESC
```

### Ejemplo 4: Consulta con dimensión temporal
```sql
-- Pregunta: "Tendencia de contratos por mes en 2025"
SELECT 
    t.month_name,
    t.year,
    COUNT(*) as contracts_count
FROM contracts_gold_2 c
JOIN DimTime t ON c.agreement_date = t.date_id
WHERE t.year = 2025
GROUP BY t.month_name, t.year, t.month
ORDER BY t.month
```

---

## 🔍 ¿Cuándo Hacer JOIN?

El sistema (LLM) decide automáticamente hacer JOIN cuando:

1. **Se mencionan nombres descriptivos**:
   - "product names" → JOIN con DimProducts
   - "province names" → JOIN con DimProvince

2. **Se necesita información de categorías**:
   - "by product category" → JOIN con DimProducts
   - "by region" → JOIN con DimProvince

3. **Se hacen análisis temporales estructurados**:
   - "by quarter" → JOIN con DimTime
   - "by month and year" → JOIN con DimTime

4. **Se agrupa por información descriptiva**:
   - "group by province" → JOIN con DimProvince para obtener nombres
   - "group by product type" → JOIN con DimProducts

**No se necesita JOIN cuando:**
- Solo se usan IDs directamente
- Solo se cuentan o suman valores numéricos
- No se necesita información descriptiva

---

## 📊 Resumen Visual

```
┌─────────────────────────────────────────────────────────┐
│              contracts_gold_2 (Fact Table)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │product_id│  │province_ │  │agreement_date│  + Medidas│
│  │    ↓     │  │   id ↓  │  │      ↓       │  (quantity│
│  └──────────┘  └──────────┘  └──────────────┘   price)  │
└─────────────────────────────────────────────────────────┘
         │              │                │
         │              │                │
    ┌────▼────┐    ┌────▼────┐    ┌──────▼──────┐
    │DimProducts│  │DimProvince│  │  DimTime    │
    │──────────│  │──────────│  │────────────│
    │product_id│  │province_ │  │  date_id    │
    │name      │  │   id     │  │  year       │
    │category  │  │name      │  │  month      │
    │type      │  │region    │  │  quarter    │
    └──────────┘  └──────────┘  └─────────────┘
```

---

## 🚀 En Tu Sistema

Tu chatbot NL → SQL utiliza un **agente LangGraph** que:

1. ✅ **Detecta automáticamente** cuándo necesita hacer JOINs usando herramientas estructuradas
2. ✅ **Obtiene los schemas** de todas las tablas de dimensiones mediante `get_dimensions_tool`
3. ✅ **Genera SQL correcto** con los JOINs apropiados usando `generate_sql_tool`
4. ✅ **Maneja errores** si alguna dimensión no existe (con caché de "no encontradas")
5. ✅ **Optimiza consultas** usando información de relaciones y caché de schemas
6. ✅ **Orquesta el flujo completo** desde la pregunta hasta la visualización usando LangGraph

**Ejemplo de pregunta que activa JOINs:**
- Usuario: "Muéstrame contratos agrupados por nombre de producto"
- Agente llama a `get_dimensions_tool`: Obtiene información de DimProducts
- Agente detecta: necesita nombres → JOIN con DimProducts
- Agente llama a `generate_sql_tool`: Genera SQL con JOIN
- SQL generado: Incluye `JOIN DimProducts ON contracts_gold_2.product_id = DimProducts.product_id`
- Agente ejecuta la consulta y recomienda visualización

---

## 📚 Conceptos Clave

- **Fact Table**: Tabla central con eventos/transacciones medibles
- **Dimension Table**: Tabla con información descriptiva
- **Foreign Key**: Columna en fact table que referencia a dimension
- **Primary Key**: Columna única en dimension que identifica cada registro
- **Star Schema**: Modelo donde fact table está en el centro rodeada de dimensiones
- **JOIN**: Operación SQL que combina datos de múltiples tablas usando claves

---

¿Tienes preguntas sobre alguna parte específica del modelo? 🤔
