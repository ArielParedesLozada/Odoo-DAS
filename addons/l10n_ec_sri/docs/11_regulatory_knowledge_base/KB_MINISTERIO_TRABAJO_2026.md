# MINISTERIO DEL TRABAJO - COMPLETE REFERENCE 2026
## SUT, Contratos, Obligaciones Laborales

**Last Verified**: 2026-01-22
**Source**: trabajo.gob.ec, Código del Trabajo

---

## 1. SALARIO BÁSICO UNIFICADO (SBU)

| Year | Amount | Legal Basis |
|:-----|:-------|:------------|
| 2024 | $460 | - |
| 2025 | $470 | - |
| **2026** | **$482** | Acuerdo MDT-2025-195 |

**Efectivo desde**: 1 de enero de 2026
**Consejo**: Consejo Nacional de Trabajo y Salarios (consensuado)

---

## 2. SISTEMA ÚNICO DE TRABAJO (SUT)

### 2.1 Portal
- URL: sut.trabajo.gob.ec
- Acceso: Con usuario y contraseña (RUC)

### 2.2 Obligaciones en SUT
| Registro | Plazo | Obligatorio |
|:---------|:------|:------------|
| Contratos de trabajo | **30 días** (antes 15) | Sí |
| Aviso de entrada IESS | 15 días | Sí |
| Aviso de salida IESS | 3 días | Sí |
| Acta de finiquito | 15 días | Sí |
| Utilidades | Abril | Sí |
| Seguridad y Salud | Anual | Sí |

### 2.3 Cambio Mayo 2026
> **IMPORTANTE**: A partir de mayo 2026, el Ministerio NO conservará documentos laborales. Los empleadores son responsables de la custodia.

---

## 3. TIPOS DE CONTRATO

| Tipo | Duración | Período Prueba |
|:-----|:---------|:---------------|
| **Indefinido** | Sin límite | 90 días |
| **Fijo** | Hasta 2 años | 90 días |
| **Eventual** | Hasta 180 días | No aplica |
| **Obra cierta** | Por proyecto | No aplica |
| **Servicios profesionales** | Variable | No aplica |

---

## 4. DÉCIMOS

### 4.1 Décimo Tercero (Bono Navideño)
| Atributo | Valor |
|:---------|:------|
| Cálculo | (Total ingresos período) / 12 |
| Período | 1 dic anterior - 30 nov actual |
| Fecha pago | **Hasta 24 de diciembre** |
| Mensualización | Solicitar antes 15 enero |

### 4.2 Décimo Cuarto (Bono Escolar)
| Atributo | Costa/Galápagos | Sierra/Amazonía |
|:---------|:----------------|:----------------|
| Monto | 1 SBU = $482 | 1 SBU = $482 |
| Período | Mar 1 - Feb 28 | Ago 1 - Jul 31 |
| Fecha pago | **Hasta 15 marzo** | **Hasta 15 agosto** |
| Mensualizado | $40.17/mes | $40.17/mes |

---

## 5. UTILIDADES (15%)

### 5.1 Distribución
| Componente | % | Criterio |
|:-----------|:--|:---------|
| **Individual** | 10% | Días trabajados |
| **Familiar** | 5% | Cargas familiares |
| **Total** | **15%** | Utilidad neta |

### 5.2 Reglas
- Fecha límite: **15 de abril**
- Cargas: Cónyuge, hijos < 21 años, discapacitados
- Registro cargas: Hasta 31 marzo en SUT
- Máximo por trabajador: 24 × SBU = **$11,568**

### 5.3 Multa por incumplimiento
- Hasta 20 SBU por trabajador afectado
- Depósito en Min. Trabajo: 30 días después

---

## 6. HORAS EXTRAS

| Tipo | Horario | Recargo | Valor/hora 2026 |
|:-----|:--------|:--------|:----------------|
| **Ordinaria** | 08:00-18:00 | Base | $2.01 |
| **Suplementaria** | 06:00-24:00 | +50% | $3.01 |
| **Extraordinaria** | 00:00-06:00, fines semana | +100% | $4.02 |
| **Nocturna** | Turno regular noche | +25% | $2.51 |

**Cálculo**: Hora = Sueldo mensual / 240

---

## 7. VACACIONES

| Atributo | Valor |
|:---------|:------|
| Días anuales | 15 días laborables |
| Después 5 años | +1 día por año adicional |
| Máximo | 30 días |
| Mínimo consecutivo | 6 días |
| Pago | Sueldo + 1/24 del anual |

---

## 8. TERMINACIÓN LABORAL

### 8.1 Tipos de Terminación
| Tipo | Indemnización |
|:-----|:--------------|
| **Renuncia voluntaria** | Liquidación básica |
| **Desahucio** | +25% sueldo × años |
| **Despido intempestivo < 3 años** | 3 meses sueldo |
| **Despido intempestivo > 3 años** | 1 mes × año (máx 25) |
| **Visto bueno** | Sin indemnización |

### 8.2 Liquidación Obligatoria
- Salario proporcional
- Décimo 13 proporcional
- Décimo 14 proporcional
- Vacaciones no gozadas
- Fondos de reserva (si retenidos)

### 8.3 Acta de Finiquito
- Registro obligatorio en SUT
- Plazo: 15 días después de terminación
- Debe incluir todos los valores

---

## 9. SEGURIDAD Y SALUD OCUPACIONAL

### Registros Obligatorios en SUT
- Responsable de seguridad y salud
- Plan de prevención de riesgos
- Programa riesgo psicosocial
- Prevención uso de drogas
- Capacitaciones
- Salas de lactancia
- Accidentes de trabajo

**Vigencia**: 12 meses cada registro

---

## 10. CÓDIGO PARA AGENTES

```python
# Ministerio del Trabajo - Parámetros 2026
SBU_2026 = 482.00
HORA_BASE = SBU_2026 / 240  # $2.01

# Décimos
DECIMO_13_DEADLINE = "2026-12-24"
DECIMO_14_COSTA = "2026-03-15"
DECIMO_14_SIERRA = "2026-08-15"

# Utilidades
UTILIDADES_DEADLINE = "2026-04-15"
UTILIDADES_10_INDIVIDUAL = 0.10
UTILIDADES_05_FAMILIAR = 0.05
UTILIDADES_MAX_PER_WORKER = SBU_2026 * 24  # $11,568

# Contrato
CONTRACT_REGISTRATION_DAYS = 30
PROBATION_DAYS = 90

# Terminación
DESPIDO_UNDER_3_YEARS = 3  # months
DESPIDO_PER_YEAR_MAX = 25  # months
DESAHUCIO_RATE = 0.25
```

---

**Classification**: Agent Knowledge Base - Labor
**Update**: Annual with SBU/law changes
