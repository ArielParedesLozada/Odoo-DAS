# USER MANUAL: ELECTRONIC INVOICING QUICK START
## Step-by-Step Guide for Creating and Sending Invoices to SRI

**Document ID**: UM-INV-001
**Audience**: End Users (Accounting, Sales)
**Version**: 1.0

---

## 1. CREATING AN INVOICE

### Step 1: Navigate to Invoicing
1. Open Odoo
2. Go to **Accounting** → **Customers** → **Invoices**
3. Click **CREATE**

### Step 2: Fill Invoice Header
| Field | What to Enter | Example |
|:------|:--------------|:--------|
| **Customer** | Select or type customer name | LA FAVORITA SAS |
| **Invoice Date** | Date of sale | 22/01/2026 |
| **Payment Terms** | Payment conditions | Immediate |

> ⚠️ **Consumidor Final**: If amount >$50, you MUST enter customer ID

### Step 3: Add Invoice Lines
1. Click **Add a line**
2. Select **Product** from dropdown
3. Enter **Quantity**
4. **Price** will auto-populate (or override)
5. **Tax** defaults to IVA 15%
6. Repeat for more products

### Step 4: Review Totals
| Field | Description |
|:------|:------------|
| Subtotal 15% | Items with 15% IVA |
| Subtotal 0% | Items with 0% IVA |
| IVA 15% | Tax amount |
| **TOTAL** | Final amount |

### Step 5: Save Draft
- Click **SAVE**
- Invoice is now in Draft status
- You can still make changes

---

## 2. SENDING TO SRI

### Step 1: Post the Invoice
1. With invoice open, click **CONFIRM**
2. System generates **Access Key** (Clave de Acceso)
3. Invoice is now Posted

### Step 2: Automatic SRI Transmission
The system automatically:
1. ✅ Signs XML with XAdES-BES
2. ✅ Sends to SRI
3. ✅ Receives authorization

### Step 3: Check Authorization Status
Look at the **SRI** tab:

| Field | Good Value | Bad Value |
|:------|:-----------|:----------|
| **Estado SRI** | AUTORIZADO | DEVUELTA/NO AUTORIZADO |
| **Número Autorización** | 37-digit number | Empty |

### What if it fails?
1. Check **Estado SRI** for error code
2. Common errors:
   - **Error 35**: Document already authorized
   - **Error 45**: XML structure error
   - **Error 28**: Date mismatch
3. Fix the issue
4. Click **Retry SRI**

---

## 3. PRINTING RIDE

### Step 1: Generate PDF
1. Open the authorized invoice
2. Click **Print** → **RIDE**
3. PDF opens in new tab

### Step 2: Email to Customer
1. Click **Send & Print**
2. Enter customer email
3. Click **Send**

### Step 3: Send via WhatsApp (AI Agent)
Say to the AI:
> "Envía el RIDE de la factura 123 por WhatsApp al cliente"

---

## 4. CREATING CREDIT NOTE

### When to Use
- Customer returns products
- Incorrect invoice needs correction
- Discount applied after sale

### Steps
1. Open the original invoice
2. Click **Add Credit Note**
3. Select reason:
   - Devolución de productos
   - Descuento
   - Error en facturación
4. Choose lines to credit (or all)
5. Click **CREATE AND POST**

---

## 5. QUICK REFERENCE

### Invoice States
| State | Color | Meaning |
|:------|:------|:--------|
| Draft | Gray | Not yet confirmed |
| Posted | Blue | Confirmed, sent to SRI |
| Paid | Green | Payment received |
| Cancelled | Red | Voided |

### Keyboard Shortcuts
| Action | Shortcut |
|:-------|:---------|
| Save | Ctrl+S |
| Edit | Ctrl+E |
| Print | Ctrl+P |

### Common Issues

| Problem | Solution |
|:--------|:---------|
| Can't find customer | Type name, press Enter to create |
| IVA not calculating | Check product tax configuration |
| SRI timeout | Wait 5 min, retry automatically |
| "No autorizado" | Check error, fix, click Retry |

---

## 6. AI ASSISTANT COMMANDS

Instead of clicking, just tell the AI:

| Say This | System Does |
|:---------|:------------|
| "Crea factura para ACME por $500" | Creates draft |
| "Agrega 10 jabones a $2 cada uno" | Adds line |
| "Confirma y envía al SRI" | Posts and transmits |
| "Envía RIDE por WhatsApp" | Sends PDF |
| "Anula esta factura" | Creates credit note |

---

**Need Help?** Contact IT Support or ask the AI: "Ayuda con facturación"
