# Odoo Custom Addons

Este repositorio contiene los módulos personalizados para la plataforma **Odoo SaaS** desplegada por AGSistemas.

## Módulos Incluidos

### 1. `l10n_ec_pos_receipt` (Facturación Electrónica en PDV)
Interviene el Punto de Venta (POS) de Odoo 17 para integrarse nativamente con la **Facturación Electrónica Ecuatoriana**. 
* Extrae la Clave de Acceso y el Número de Autorización al confirmar un pago.
* Almacena datos en el historial local del navegador para permitir la reimpresión exacta de tickets.
* Evita problemas de impresión blanca incrustando la información generada antes del envío asincrónico por CRON al SRI.

### 2. `saas_invoice_limit` (Límite Mensual SaaS)
Módulo administrativo que permite establecer e imponer una cuota de facturas mensuales por compañía.
* Restringe validaciones programáticas, manuales y directamente desde la pantalla de pagos del Punto de Venta al alcanzar el nivel contratado de facturas emitidas este mes.
* Añade contadores en vivo a la ficha de la compañía mostrando uso y disponibilidad.

---
**Desarrollado y mantenido por:** [AGSistemas Informáticos]
