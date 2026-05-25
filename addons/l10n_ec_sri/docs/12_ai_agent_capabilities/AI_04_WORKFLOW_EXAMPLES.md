# AI AGENT: WORKFLOW EXAMPLES
## AI_04 - Complete AI Automation Scenarios

**Document ID**: AI-004 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: AI Architect

---

## 1. VOICE-TO-PURCHASE ORDER

```
User: "Hazme una orden de compra a Proveedor ABC"
AI: "¿Qué productos necesitas?"
User: [Sends photo of product list]
AI: [OCR extracts: Widget Pro x50, Gadget Plus x25]
AI: "Encontré 2 productos. Widget Pro 50 unidades, Gadget Plus 25 unidades. ¿Confirmo?"
User: "Sí, confirma"
AI: → mcp.call("purchase/create_order", {...})
AI: "Orden PO-2026-0042 creada por $3,750. ¿La envío al proveedor?"
```

---

## 2. AI COLLECTION SEQUENCE

```
Day 1 (Due Date):
  WhatsApp: "Hola Juan, recordatorio: Factura F-001 por $500 vence hoy."

Day 3:
  SMS: "Su factura F-001 de $500 está vencida."

Day 7:
  WhatsApp: "Estimado Juan, su factura F-001 tiene 7 días vencida.
             ¿Podemos coordinar el pago? Responda a este mensaje."

Day 15:
  Call Request: "AI escalates to human agent"
```

---

## 3. AI INVOICE FROM VOICE

```
User: "Factura 500 dólares a Empresa XYZ por servicios de consultoría"
AI: → mcp.read("odoo://partners/search?q=Empresa XYZ")
AI: → mcp.call("invoice/create", {
        partner_id: 42,
        lines: [{description: "Servicios de consultoría", amount: 500}],
        tax: "iva_15"
     })
AI: "Factura 001-001-000123 creada por $575 (IVA incluido). ¿La envío al SRI?"
User: "Sí"
AI: → mcp.call("invoice/send_sri", {invoice_id: 123})
AI: "Autorizada. RIDE enviado a cliente@xyz.com"
```

---

## 4. AI LIQUIDATION CALCULATOR

```
User: "Calcula la liquidación de María Pérez, renuncia después de 3 años"
AI: → mcp.read("odoo://employees/search?q=María Pérez")
AI: → mcp.call("payroll/calculate_liquidation", {
        employee_id: 15,
        termination_type: "renuncia",
        last_day: "2026-01-31"
     })
AI: "Liquidación María Pérez:
     - Sueldo proporcional: $800 (20 días)
     - Décimo 13 proporcional: $100
     - Décimo 14 proporcional: $40
     - Vacaciones (8 días): $320
     - Total: $1,260
     ¿Genero el Acta de Finiquito?"
```

---

## 5. AI DAILY BRIEFING

```
Every morning at 8:00 AM:
AI: "Buenos días. Resumen del día:
     📊 Ventas ayer: $12,500
     💰 Cuentas por cobrar vencidas: $8,200 (5 facturas)
     📅 Hoy vence: Form 103 IR, Planilla IESS
     ⚠️ Stock bajo: Widget Pro (5 unidades)
     ¿Quieres que active la cobranza automática?"
```

---

## 6. AI TAX COMPLIANCE MONITOR

```
AI (automated check every week):
→ Check SRI deadlines
→ Check IESS submission status
→ Verify all invoices authorized
→ Check withholding compliance (5-day rule)

Alert: "⚠️ 3 facturas recibidas hace 4 días sin retención.
        Límite mañana. ¿Genero las retenciones?"
User: "Sí"
AI: → mcp.call("withholding/create_batch", {...})
AI: "3 retenciones generadas y enviadas al SRI. Todas autorizadas."
```

---

**AI Workflow Classification**: ISO 9001:2015 Controlled
