# SRS-ECOMMERCE-SOMATECH-ECUADOR
> **Software Requirements Specification**
> **ISO/IEC 29148:2018 Compliant**
> **Version**: 3.0 | **Date**: 2026-01-24

---

## MULTI-PERSONA ANALYSIS

> [!IMPORTANT]
> **As per Vibe Coding Rules, this document has been reviewed by ALL personas simultaneously.**

### 🧑‍💻 PhD Software Developer Analysis
- **Architecture**: Headless commerce (Lit → Django → Odoo) is optimal for decoupling
- **Risk**: XML-RPC latency between Django-Odoo may impact checkout UX
- **Recommendation**: Implement async queues for non-critical Odoo calls
- **Pattern**: Repository pattern for service layer, Reactive Controllers for state

### 🔍 PhD QA Engineer Analysis
- **Test Strategy**: E2E with Playwright, Unit with Vitest
- **Critical Paths**: Cart→Checkout→SRI Invoice must have 100% coverage
- **Edge Cases**: Guest cart merge, stock race conditions, SRI timeout handling
- **Automation**: CI/CD with Vite test runner before deployment

### 🔐 Security Auditor Analysis
- **OWASP Top 10 Review**:
  - XSS: Mitigated by Lit's automatic escaping
  - CSRF: Django provides tokens, frontend must include
  - Injection: ORM prevents SQL injection
- **PCI DSS**: Phase 2 payment gateway requires SAQ-A compliance
- **Ecuador LOPDP**: Personal data (RUC/Cédula) requires explicit consent

### 🎨 UX Consultant Analysis
- **Conversion Optimization**:
  - One-page checkout reduces abandonment by 20%
  - Cart drawer > cart page for quick adds
  - Guest checkout is MANDATORY (35% of users abandon on forced registration)
- **Mobile-First**: 60%+ Ecuador users are mobile
- **Accessibility**: WCAG 2.1 AA for inclusive commerce

### ⚡ Performance Engineer Analysis
- **Core Web Vitals Targets**:
  - LCP < 2.5s (product images lazy-loaded)
  - FID < 100ms (minimal main thread blocking)
  - CLS < 0.1 (skeleton loaders prevent layout shift)
- **Bundle**: Tree-shake Lit, code-split by route
- **CDN**: Static assets on CloudFront/Cloudflare

### 💼 CFO/Legal Analysis
- **Ecuador Tax Compliance**:
  - IVA 15% must be transparent in all prices
  - SRI invoice mandatory for B2C sales
  - RUC validation for B2B transactions
- **LOPDP**: Privacy policy required, data retention limits
- **Returns**: Consumer protection law (14-day return period)

### 🏗️ Django/Ninja Architect Analysis
- **API Design**: RESTful with Django Ninja async handlers
- **Odoo Bridge**: Use connection pooling for XML-RPC
- **Caching**: Redis for product catalog (5-min TTL)
- **Rate Limiting**: 100 req/min per IP on auth endpoints

---

## 1. Executive Summary

| Aspect | Value |
|--------|-------|
| **Benchmark** | WooCommerce + Shopify feature parity |
| **Market** | Ecuador B2C (nationwide) |
| **Currency** | USD |
| **Tax** | IVA 15% included |
| **Differentiator** | Native SRI electronic invoicing |

---

## 2. Feature Modules with Persona Sign-Off

### M01: Product Catalog

| ID | Requirement | UX | QA | Security |
|----|-------------|----|----|----------|
| FR-01.01 | Product grid with pagination | ✅ | ✅ | ✅ |
| FR-01.02 | Card: image, name, price, rating, stock | ✅ | ✅ | ✅ |
| FR-01.03 | Multiple images per product (gallery) | ✅ | ✅ | ✅ (XSS-safe) |
| FR-01.04 | Zoom on image hover | ✅ | ⏳ | ✅ |
| FR-01.05 | Nested category hierarchy | ✅ | ✅ | ✅ |
| FR-01.06 | Product tags | ✅ | ⏳ | ✅ |
| FR-01.07 | Related products section | ✅ (conversion) | ⏳ | ✅ |
| FR-01.08 | Recently viewed products | ✅ | ⏳ | ✅ (localStorage) |
| FR-01.09 | "New" badge (< 30 days) | ✅ | ✅ | ✅ |
| FR-01.10 | "Sale" badge with % discount | ✅ (FOMO) | ✅ | ✅ |
| FR-01.11 | Quick view modal | ✅ | ⏳ | ✅ |

### M02: Product Variations

| ID | Requirement | Dev | Perf |
|----|-------------|-----|------|
| FR-02.01 | Variants (size, color) | Django API | ✅ |
| FR-02.02 | Variant-specific pricing | Odoo product.product | ✅ |
| FR-02.03 | Variant-specific images | Image mapping | ✅ |
| FR-02.04 | Variant-specific stock | qty_available per variant | ✅ |
| FR-02.05 | Variant selector (dropdowns/swatches) | Lit component | ✅ |
| FR-02.06 | Color swatches with preview | CSS backgrounds | ✅ |

### M03: Search & Filtering

| ID | Requirement | Perf Impact | Index Required |
|----|-------------|-------------|----------------|
| FR-03.01 | Search bar in header | Low | - |
| FR-03.02 | Autocomplete (debounced 300ms) | Medium | product.name |
| FR-03.03 | Search: name, SKU, description | High | Full-text index |
| FR-03.04 | Typo tolerance | High | Elasticsearch (Phase 2) |
| FR-03.05 | Filter by category | Low | categ_id |
| FR-03.06 | Filter by price range (slider) | Low | list_price |
| FR-03.07 | Filter by availability | Low | qty_available > 0 |
| FR-03.08 | Filter by rating | Medium | Computed field |
| FR-03.09 | Filter by attributes | Medium | Attribute index |
| FR-03.10 | Sort options (5 types) | Low | Combined index |

### M04: Shopping Cart

| ID | Requirement | Security Review | Legal Review |
|----|-------------|-----------------|--------------|
| FR-04.01 | Add to cart button | ✅ CSRF protected | ✅ |
| FR-04.02 | Quick add from grid | ✅ | ✅ |
| FR-04.03 | Cart sidebar/drawer | ✅ XSS-safe | ✅ |
| FR-04.04 | Cart page full details | ✅ | ✅ Price accuracy |
| FR-04.05 | Update quantity | ✅ Stock validation | ✅ |
| FR-04.06 | Remove item | ✅ | ✅ |
| FR-04.07 | IVA breakdown | ✅ | ✅ REQUIRED BY SRI |
| FR-04.08 | Estimated shipping | ✅ | ✅ |
| FR-04.09 | Persistent cart (logged-in) | ✅ Server-side | ✅ GDPR consent |
| FR-04.10 | localStorage cart (guest) | ✅ No PII | ✅ |

### M05-M06: Wishlist & Accounts

| ID | Requirement | Legal | CFO |
|----|-------------|-------|-----|
| FR-05.01 | Wishlist feature | ✅ Optional | ✅ Retention KPI |
| FR-06.01 | Email/password registration | ✅ LOPDP | ✅ |
| FR-06.03 | Ecuador ID (RUC/Cédula) | ✅ REQUIRED for SRI | ✅ Tax compliance |
| FR-06.05 | Password reset | ✅ Secure token | ✅ |
| FR-06.13 | Download invoices (PDF) | ✅ | ✅ REQUIRED |

### M07: Checkout

| ID | Requirement | UX Score | Security | Legal |
|----|-------------|----------|----------|-------|
| FR-07.01 | Guest checkout | 10/10 | ✅ | ✅ |
| FR-07.02 | Account creation during checkout | 7/10 | ✅ | ✅ Consent |
| FR-07.03-05 | Address forms | 8/10 | ✅ No logging | ✅ |
| FR-07.06 | Ecuador province/city | 9/10 | ✅ | ✅ |
| FR-07.11 | Coupon code | 8/10 | ✅ Rate limit | ✅ |
| FR-07.12 | Terms checkbox | REQUIRED | ✅ | ✅ MANDATORY |
| FR-07.13 | SRI invoice data | 8/10 | ✅ Encrypted | ✅ TAX LAW |
| FR-07.14 | Consumidor Final option | 9/10 | ✅ | ✅ SRI RULE |

### M08: Payment Gateways

| ID | Gateway | Phase | PCI DSS | CFO Approved |
|----|---------|-------|---------|--------------|
| FR-08.01 | Cash on Delivery | 1 | N/A | ✅ |
| FR-08.02 | Bank Transfer | 1 | N/A | ✅ |
| FR-08.03 | DeUna QR | 2 | SAQ-A | ✅ Ecuador |
| FR-08.04 | PayPhone | 2 | SAQ-A | ✅ Ecuador |
| FR-08.05 | PayPal | 2 | SAQ-A | ✅ |
| FR-08.06 | Credit Card | 3 | SAQ-A-EP | ⚠️ Higher fees |

### M16: Ecuador SRI Integration

| ID | Requirement | Legal Mandate | Penalty Risk |
|----|-------------|---------------|--------------|
| FR-16.01 | Collect RUC/Cédula | Ley RO 587 | ✅ |
| FR-16.02 | Consumidor Final | SRI Resolución | $500+ fine |
| FR-16.03 | IVA 15% display | Tax Code | $1000+ fine |
| FR-16.04 | Auto invoice generation | Law | Business closure |
| FR-16.05 | XAdES-BES signature | SRI Tech Spec | Rejection |
| FR-16.06 | SRI SOAP submission | Law | Rejection |
| FR-16.07 | Authorization display | Law | $500+ fine |
| FR-16.08 | RIDE PDF | Customer right | Reputation |
| FR-16.09 | Invoice email | Best practice | - |

---

## 3. Non-Functional Requirements

### Performance (⚡ Performance Engineer Sign-Off)

| ID | Metric | Target | Current | Risk |
|----|--------|--------|---------|------|
| NFR-01 | FCP | < 1.8s | TBD | Medium |
| NFR-02 | LCP | < 2.5s | TBD | High (images) |
| NFR-03 | TTI | < 3.5s | TBD | Low |
| NFR-04 | CLS | < 0.1 | TBD | Low (skeletons) |
| NFR-05 | API p95 | < 500ms | TBD | Medium (Odoo) |
| NFR-06 | JS Bundle | < 150KB | TBD | Low |

### Security (🔐 Security Auditor Sign-Off)

| ID | Requirement | OWASP | Status |
|----|-------------|-------|--------|
| NFR-10 | HTTPS (TLS 1.3) | A3 | ✅ Nginx |
| NFR-11 | CSRF tokens | A5 | ✅ Django |
| NFR-12 | XSS prevention | A7 | ✅ Lit |
| NFR-13 | SQL injection | A3 | ✅ ORM |
| NFR-14 | Rate limiting | A10 | ⏳ PENDING |
| NFR-15 | Password hashing | A2 | ✅ Argon2 |

---

## 4. PMI Work Breakdown Structure

### Timeline Overview

```
Phase 1: Foundation     [========] Sprints 1-2  (DONE)
Phase 2: Catalog        [========] Sprints 3-4  (DONE)
Phase 3: Cart/Checkout  [........] Sprints 5-6
Phase 4: Accounts       [........] Sprints 7-8
Phase 5: Enhancements   [........] Sprints 9-10
Phase 6: SRI Polish     [........] Sprints 11-12
```

### Phase 3: Cart & Checkout (NEXT)

| WBS | Task | Owner | Days | Dependencies |
|-----|------|-------|------|--------------|
| 3.1 | Cart Drawer | Dev | 2 | - |
| 3.2 | Cart Page | Dev | 2 | 3.1 |
| 3.3 | Coupon System | Dev | 2 | 3.2 |
| 3.4 | Checkout Form | Dev | 4 | 3.2 |
| 3.5 | Payment Selection | Dev | 2 | 3.4 |
| 3.6 | SRI Data Fields | Dev | 1 | 3.4 |
| 3.7 | Order Confirmation | Dev | 1 | 3.5, 3.6 |
| 3.8 | E2E Tests | QA | 2 | 3.7 |

---

## 5. Acceptance Criteria (QA Engineer)

| Milestone | Test Case | Pass Criteria |
|-----------|-----------|---------------|
| M1-Catalog | TC-01 | Products load in < 2s |
| M2-Search | TC-02 | Autocomplete in < 300ms |
| M3-Cart | TC-03 | Add/remove updates badge |
| M4-Checkout | TC-04 | Guest completes order |
| M5-SRI | TC-05 | Invoice has authorization # |

---

## 6. Risk Register (PMI)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Odoo XML-RPC latency | Medium | High | Async queues, caching |
| SRI downtime | Medium | Critical | Retry with backoff |
| Payment gateway delays | Low | High | Phase 2 rollout |
| Mobile performance | Medium | Medium | Bundle optimization |

---

## 7. Revision History

| Ver | Date | Author | Changes |
|-----|------|--------|---------|
| 1.0 | 2026-01-24 | Antigravity | Initial |
| 2.0 | 2026-01-24 | Antigravity | WooCommerce/Shopify parity |
| 3.0 | 2026-01-24 | Antigravity | **Multi-Persona Analysis added** |
