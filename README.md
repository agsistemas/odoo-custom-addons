# Odoo Custom Addons

Este repositorio contiene los módulos exclusivos desarrollados a la medida para la plataforma **Odoo SaaS Ecuatoriana** gestionada por AGSistemas Informáticos.

## Catálogo de Módulos

### 1. Facturación Electrónica en Punto de Venta (`l10n_ec_pos_receipt`)
Este módulo mejora la experiencia de venta en cajeros y mostradores (PDV) permitiéndoles entregar comprobantes válidos inmediatamente sin hacer esperar al cliente.
* **Recibos Completos al Instante**: Agrega automáticamente la Clave de Acceso del SRI al ticket térmico en el segundo exacto en que se concreta la venta.
* **Garantía de Reimpresión**: Permite a los cajeros buscar una orden pasada de hace días o meses y volver a reimprimir el ticket térmico manteniendo intactos y visibles todos los datos electrónicos de la factura original.
* **Reparación de PDFs en Blanco**: Soluciona el problema de Odoo que generaba las facturas RIDE (en PDF) sin la clave de acceso ni código de barras si estas se descargaban muy rápido.

### 2. Límite de Intecenciones SaaS (`saas_invoice_limit`)
Este es un módulo de administración y control diseñado para ayudarte a gestionar suscripciones, cobros y uso comercial de tus diferentes clientes dentro del software SaaS.
* **Restricción de Uso**: Te permite establecer un techo o cantidad máxima de facturas que una empresa puede realizar en un mes calendario.
* **Bloqueo Inteligente**: Si un cliente se queda sin facturas, el módulo le impedirá confirmar más pagos tanto en el menú administrativo como directamente en la caja del Punto de Venta, invitándole a contactar a AGSistemas.
* **Contadores en Vivo**: Añade información en directo dentro de los ajustes de Odoo indicando a simple vista cuántas facturas ha gastado el comercio este mes y cuántas le restan por emitir.

---
**Desarrollado y mantenido por:** [AGSistemas Informáticos]
