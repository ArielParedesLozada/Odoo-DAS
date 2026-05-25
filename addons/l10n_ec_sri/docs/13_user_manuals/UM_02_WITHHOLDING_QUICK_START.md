# USER MANUAL: WITHHOLDING QUICK START
## UM_02 - Emisión de Comprobantes de Retención

**Document ID**: UM-002 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Training Lead | **Audience**: Accounts Payable Staff

---

## 1. ¿QUÉ ES UNA RETENCIÓN?

Una **Retención** es un comprobante electrónico emitido cuando paga a un proveedor, reteniendo parte del impuesto (IR y/o IVA) que debe ser entregado al SRI.

> [!IMPORTANT]
> Debe emitirse **dentro de 5 días** desde la fecha de la factura del proveedor.

---

## 2. PASOS PARA EMITIR RETENCIÓN

### Paso 1: Abrir Factura del Proveedor

1. Ir a **Contabilidad > Proveedores > Facturas**
2. Buscar y abrir la factura registrada
3. Verificar que esté en estado **"Publicada"**

### Paso 2: Crear Retención

1. Clic botón **"Crear Retención"** (arriba derecha)
2. El sistema abre formulario de retención enlazado

### Paso 3: Verificar Datos del Proveedor

| Campo | Acción |
|:------|:-------|
| RUC/Cédula | Verificar correcto |
| Razón Social | Verificar correcto |
| Tipo Contribuyente | Determina tasas aplicables |

### Paso 4: Agregar Líneas de Retención

#### Retención IR (Impuesto a la Renta)

| Si el proveedor es... | Código | % |
|:----------------------|:-------|:--|
| Servicios profesionales | 303 | 10% |
| Servicios generales | 312 | 10% |
| Compra de bienes | 310 | 1% |
| Arrendamiento | 320 | 8% |

#### Retención IVA

| Si su empresa es... | % Bienes | % Servicios |
|:--------------------|:---------|:------------|
| Contribuyente Especial | 30% | 70% |
| Empresa Normal | 30% | 70% |
| Sociedad | 30% | 70% |

### Paso 5: Revisar Totales

```
Base Imponible IR:     $1,000.00
Retención IR (10%):       $100.00

Base Imponible IVA:      $150.00
Retención IVA (70%):     $105.00

TOTAL A RETENER:         $205.00
```

### Paso 6: Confirmar y Enviar al SRI

1. Clic **"Confirmar"**
2. Sistema genera XML y firma electrónica
3. Transmite automáticamente al SRI
4. Esperar autorización (segundos)

### Paso 7: Verificar Estado

| Estado | Significado |
|:-------|:------------|
| ✅ Autorizado | Listo para entregar |
| 🔄 Enviado | Esperando respuesta SRI |
| ❌ Rechazado | Ver errores y corregir |

### Paso 8: Entregar al Proveedor

1. Clic **"Enviar por Email"**
2. Sistema envía RIDE (PDF) adjunto
3. O imprimir para entrega física

---

## 3. CASOS ESPECIALES

### Retención a Persona Natural No Obligada

- SI presta servicios profesionales → Retener 10% IR
- SI es arrendamiento → Retener 8% IR

### Retención $0 (Exento)

Si el proveedor es:
- Empresa pública
- Contribuyente RISE
- Organismo internacional

→ Crear retención con valor $0 para registro

### Factura con Múltiples Conceptos

Agregar una línea por cada tipo de retención aplicable.

---

## 4. REGLA DE LOS 5 DÍAS

> [!WARNING]
> La retención debe emitirse máximo 5 días después de la factura.

| Fecha Factura | Fecha Límite Retención |
|:--------------|:-----------------------|
| 1 de enero | 6 de enero |
| 15 de enero | 20 de enero |

El sistema muestra **alerta amarilla** a partir del día 4.

---

## 5. USANDO COMANDOS DE VOZ (AI)

```
"Crear retención para factura de Proveedor ABC"
"Aplicar retención 10% servicios a la última factura"
"Mostrar retenciones pendientes de envío"
```

---

## 6. RESOLUCIÓN DE ERRORES

| Error | Solución |
|:------|:---------|
| "Clave de acceso inválida" | Verificar certificado digital |
| "RUC no corresponde" | Corregir RUC del proveedor |
| "Factura ya tiene retención" | Anular retención anterior |
| "Fuera de plazo" | Requiere justificación |

---

## 7. PREGUNTAS FRECUENTES

**¿Puedo modificar una retención autorizada?**
No. Debe anularla y crear una nueva.

**¿Qué pasa si el proveedor rechaza la retención?**
Verificar los códigos aplicados con el SRI.

**¿Cómo anulo una retención?**
Contabilidad > Retenciones > Seleccionar > Anular

---

**Manual Classification**: ISO 9001:2015 Controlled
