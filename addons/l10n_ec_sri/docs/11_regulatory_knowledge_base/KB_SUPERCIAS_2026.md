# SUPERINTENDENCIA DE COMPAÑÍAS - REFERENCE 2026
## Estados Financieros, Obligaciones Societarias

**Last Verified**: 2026-01-22
**Source**: supercias.gob.ec

---

## 1. OVERVIEW

La Superintendencia de Compañías, Valores y Seguros (SCVS) regula:
- Compañías anónimas
- Compañías de responsabilidad limitada
- Compañías extranjeras
- Mercado de valores

---

## 2. ESTADOS FINANCIEROS ANUALES

### 2.1 Documentos Requeridos
| Documento | Obligatorio |
|:----------|:------------|
| Estado de Situación Financiera | ✅ |
| Estado de Resultados Integral | ✅ |
| Estado de Flujos de Efectivo | ✅ |
| Estado de Cambios en Patrimonio | ✅ |
| Notas Explicativas | ✅ |
| Informe del Representante Legal | ✅ |
| Informe de Comisarios | Si aplica |
| Formulario 101 SRI | ✅ |

### 2.2 Plazos de Presentación
| Noveno Dígito RUC | Fecha Límite |
|:------------------|:-------------|
| 1 | Abril 10 |
| 2 | Abril 12 |
| 3 | Abril 14 |
| 4 | Abril 16 |
| 5 | Abril 18 |
| 6 | Abril 20 |
| 7 | Abril 22 |
| 8 | Abril 24 |
| 9 | Abril 26 |
| 0 | Abril 28 |

**Máximo absoluto**: 30 de abril

### 2.3 Portal de Presentación
- URL: www.supercias.gob.ec
- Formato: Electrónico
- Requiere: Firma electrónica del representante legal

---

## 3. NORMAS CONTABLES

### 3.1 NIIF Completas
Aplica a:
- Compañías que cotizan en bolsa
- Compañías grandes (activos > $4M o ventas > $5M)
- Compañías con + 200 empleados

### 3.2 NIIF PYMES
Aplica a:
- Pequeñas y medianas empresas
- Activos < $4M y ventas < $5M
- Menos de 200 empleados

---

## 4. CONTRIBUCIÓN SOCIETARIA

### 4.1 Cálculo
| Base | Tasa |
|:-----|:-----|
| Activos totales | 1‰ (uno por mil) |
| Mínimo | $300 |
| Máximo | $50,000 |

### 4.2 Pago
- Plazo: Junto con estados financieros
- Forma: Depósito o transferencia

---

## 5. AUDITORÍA EXTERNA

### 5.1 Obligatoria Para
| Criterio | Umbral |
|:---------|:-------|
| Activos totales | > $500,000 |
| Ventas brutas | > $1,000,000 |
| Empleados | > 50 |

### 5.2 Requisitos del Auditor
- Inscrito en el Registro de Auditores de la Supercias
- Cumplir normativa de independencia

---

## 6. CONSTITUCIÓN DE COMPAÑÍAS

### 6.1 Capital Mínimo
| Tipo | Capital |
|:-----|:--------|
| Compañía Limitada | $400 |
| Sociedad Anónima | $800 |

### 6.2 Proceso
1. Reserva de denominación
2. Escritura pública
3. Aprobación Supercias
4. Inscripción Registro Mercantil
5. Obtención RUC

---

## 7. PLAN DE CUENTAS (ESTRUCTURA NIIF)

```
1. ACTIVO
   1.01 ACTIVO CORRIENTE
      1.01.01 Efectivo y Equivalentes
      1.01.02 Activos Financieros
      1.01.03 Inventarios
      1.01.04 Servicios y Otros Pagos Anticipados
      1.01.05 Activos por Impuestos Corrientes
   1.02 ACTIVO NO CORRIENTE
      1.02.01 Propiedades, Planta y Equipo
      1.02.02 Propiedades de Inversión
      1.02.03 Activos Intangibles
      1.02.04 Activos por Impuestos Diferidos
2. PASIVO
   2.01 PASIVO CORRIENTE
      2.01.01 Cuentas y Documentos por Pagar
      2.01.02 Obligaciones con Instituciones Financieras
      2.01.03 Provisiones
      2.01.04 Pasivos por Impuestos Corrientes
   2.02 PASIVO NO CORRIENTE
3. PATRIMONIO
   3.01 Capital
   3.02 Reservas
   3.03 Resultados Acumulados
   3.04 Resultados del Ejercicio
4. INGRESOS
5. COSTOS
6. GASTOS
```

---

## 8. SANCIONES

| Infracción | Multa |
|:-----------|:------|
| No presentar estados financieros | 1-10 SBU |
| Información falsa | 5-20 SBU + responsabilidad penal |
| No auditoría obligatoria | 5-15 SBU |

---

## 9. CÓDIGO PARA AGENTES

```python
# Supercias - Parámetros 2026
ESTADOS_FINANCIEROS_DEADLINE = "2026-04-30"
CONTRIBUCION_MIN = 300.00
CONTRIBUCION_MAX = 50000.00
CONTRIBUCION_RATE = 0.001  # 1 por mil

# Umbrales para Auditoría
AUDITORIA_ACTIVOS = 500000
AUDITORIA_VENTAS = 1000000
AUDITORIA_EMPLEADOS = 50

# Capital mínimo
CAPITAL_LTDA = 400
CAPITAL_SA = 800

# Umbrales NIIF PYMES
NIIF_PYMES_ACTIVOS = 4000000
NIIF_PYMES_VENTAS = 5000000
NIIF_PYMES_EMPLEADOS = 200
```

---

**Classification**: Agent Knowledge Base - Supercias
**Update**: Annual with regulatory changes
