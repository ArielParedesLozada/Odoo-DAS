# USER MANUAL: PAYROLL QUICK START
## UM_03 - Procesamiento de Nómina Ecuador

**Document ID**: UM-003 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Training Lead | **Audience**: HR/Payroll Staff

---

## 1. CALENDARIO DE NÓMINA

| Actividad | Fecha | Responsable |
|:----------|:------|:------------|
| Cierre de novedades | 25 de cada mes | HR |
| Procesamiento nómina | 27-28 de cada mes | Payroll |
| Pago de sueldos | Último día hábil | Finance |
| Envío planilla IESS | Hasta el 15 siguiente | Payroll |

---

## 2. PROCESO MENSUAL

### Paso 1: Revisar Novedades

1. Ir a **RRHH > Nómina > Novedades del Período**
2. Verificar:
   - ✅ Nuevos ingresos registrados
   - ✅ Salidas/renuncias procesadas
   - ✅ Horas extras aprobadas
   - ✅ Ausencias justificadas
   - ✅ Préstamos quirografarios

### Paso 2: Generar Roles de Pago

1. Ir a **RRHH > Nómina > Lotes de Nómina**
2. Clic **"Crear"**
3. Seleccionar:
   - Período: Ej. "Enero 2026"
   - Estructura: "EC_STANDARD"
   - Empleados: Todos o selección
4. Clic **"Generar Roles"**

### Paso 3: Revisar Cálculos

Para cada empleado verificar:

| Concepto | Fórmula |
|:---------|:--------|
| Sueldo | Base del contrato |
| H. Extras 50% | Horas × Hora × 1.5 |
| H. Extras 100% | Horas × Hora × 2.0 |
| IESS Personal | Base × 9.45% |
| Imp. Renta | Según tabla SRI |
| **Neto a Recibir** | Ingresos - Deducciones |

### Paso 4: Aprobar Nómina

1. Clic **"Confirmar Lote"**
2. Sistema genera asientos contables
3. Estado cambia a "Listo para Pago"

### Paso 5: Procesar Pago

1. Ir a **Contabilidad > Pagos > Pagos Masivos**
2. Seleccionar lote de nómina
3. Generar archivo para banco
4. Autorizar transferencias

---

## 3. CÁLCULOS IMPORTANTES

### IESS (Seguro Social)

```
Sueldo: $1,200.00
─────────────────────────
Aporte Personal (9.45%):  $113.40 (descuento)
Aporte Patronal (12.15%): $145.80 (gasto empresa)
```

### Décimo Tercer Sueldo

```
Período: Dic-Nov
Cálculo: Suma sueldos ÷ 12
Pago: Hasta 24 de Diciembre

Ejemplo: 12 meses × $1,000 = $12,000 ÷ 12 = $1,000
```

### Décimo Cuarto Sueldo

```
Monto: 1 SBU = $482 (2026)
Pago Sierra: Hasta 15 de Abril
Pago Costa: Hasta 15 de Agosto
```

### Fondos de Reserva

```
Requisito: +13 meses de servicio
Cálculo: Sueldo × 8.33%
Opciones: Mensualizado o Acumulado en IESS
```

---

## 4. GENERACIÓN PLANILLA IESS

### Paso 1: Abrir Asistente

1. Ir a **RRHH > Reportes > Generar Planilla IESS**
2. Seleccionar mes/año

### Paso 2: Revisar Datos

- Todos los empleados activos
- Novedades (EN, SA, AU, RE)
- Días trabajados correctos

### Paso 3: Exportar Archivo

1. Clic **"Generar Archivo"**
2. Descargar CSV/TXT
3. Subir al portal IESS

---

## 5. LIQUIDACIÓN DE EMPLEADO

### Paso 1: Iniciar Liquidación

1. Ir a **RRHH > Empleados > [Empleado]**
2. Clic **"Terminar Contrato"**
3. Seleccionar motivo:
   - Renuncia Voluntaria
   - Despido Intempestivo
   - Desahucio
   - Mutuo Acuerdo

### Paso 2: Calcular Valores

Sistema calcula automáticamente:

| Concepto | Fórmula |
|:---------|:--------|
| Sueldo proporcional | Días trabajados |
| D13 proporcional | Meses ÷ 12 |
| D14 proporcional | Meses ÷ 12 |
| Vacaciones | Días no gozados |
| Fondos Reserva | Si acumulados |
| Indemnización | Según tipo terminación |

### Paso 3: Generar Acta de Finiquito

1. Clic **"Generar Finiquito"**
2. Imprimir y firmar
3. Registrar en SUT (Min. Trabajo)

---

## 6. COMANDOS DE VOZ (AI)

```
"Calcular liquidación de Juan Pérez por renuncia"
"Mostrar nómina pendiente de este mes"
"¿Cuánto es el décimo tercero de María García?"
"Generar planilla IESS de enero"
```

---

## 7. ERRORES COMUNES

| Error | Solución |
|:------|:---------|
| IESS no cuadra | Verificar base de aportación |
| Días incorrectos | Revisar novedades/ausencias |
| Fondos Reserva $0 | Verificar meses de servicio |
| Error planilla IESS | Validar cédulas en sistema IESS |

---

## 8. FECHAS IMPORTANTES 2026

| Fecha | Obligación |
|:------|:-----------|
| 15 cada mes | Planilla IESS |
| 15 Abril | D14 Sierra + Utilidades |
| 15 Agosto | D14 Costa |
| 24 Diciembre | D13 Nacional |

---

**Manual Classification**: ISO 9001:2015 Controlled
