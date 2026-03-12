// Copyright (c) 2025, aet and contributors
// License: GNU General Public License v3. See license.txt

/**
 * Import Reservation functionality for Sales Invoice
 * Allows importing reservation data into Sales Invoice
 */

frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Add "Importar Reserva" button under "Calcular" menu
        if (!frm.doc.__islocal) return;
        
        frm.add_custom_button(__("Importar Reserva"), function() {
            hermes_reservation_selector.show_dialog(frm);
        }, __("Calcular"));
    }
});

// Namespace for reservation selector functions
var hermes_reservation_selector = {
    // Get CSS styles for reservation selector
    getStyles: function() {
        return `<style>
            .res-container { width:100%; max-width:1100px; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
            .modal-dialog { width:70% !important; max-width:1100px !important; }
            .modal-body { max-height:70vh; overflow-y:auto; }
            .res-card { display:flex; flex-wrap:wrap; align-items:center; padding:12px 15px; margin-bottom:8px; border-radius:8px; background:#fff; border:1px solid #e5e7eb; transition:all 0.2s; cursor:pointer; }
            .res-card:hover { background:#f0f9ff; border-color:#3b82f6; transform:translateX(5px); box-shadow:0 4px 12px rgba(0,0,0,0.15); }
            .res-card:nth-child(even) { background:#fafafa; }
            .res-card:nth-child(even):hover { background:#f0f9ff; }
            .res-id-col { min-width:70px; width:70px; flex-shrink:0; margin-right:8px; }
            .res-id { font-weight:700; font-size:13px; color:#1e40af; }
            .res-customer-col { min-width:150px; flex-grow:1; margin-right:8px; }
            .res-customer { color:#1f2937; font-weight:600; font-size:13px; }
            .res-dates-col { min-width:120px; flex-shrink:0; margin-right:8px; }
            .res-date { color:#4b5563; font-size:11px; }
            .res-date-label { font-size:9px; color:#9ca3af; text-transform:uppercase; }
            .res-amount-col { min-width:80px; text-align:right; flex-shrink:0; margin-right:8px; }
            .res-amount { font-weight:700; font-size:13px; color:#059669; }
            .res-paid { font-size:10px; color:#6b7280; }
            .res-status-col { min-width:100px; text-align:center; flex-shrink:0; margin-right:8px; }
            .res-combo-col { min-width:100px; flex-shrink:0; margin-right:8px; }
            .res-combo { font-weight:700; font-size:12px; color:#dc2626; background:#fee2e2; padding:4px 8px; border-radius:4px; display:inline-block; margin:2px; }
            .res-room-col { min-width:180px; flex-grow:2; flex-shrink:0; }
            .res-room { font-weight:600; font-size:12px; color:#7c3aed; background:#f3e8ff; padding:4px 8px; border-radius:4px; display:inline-block; margin:2px; }
            .res-badge { display:inline-block; padding:4px 10px; border-radius:4px; font-size:10px; font-weight:700; color:white; text-transform:uppercase; }
            .res-header { display:flex; flex-wrap:wrap; padding:10px 15px; background:linear-gradient(135deg,#1e3a8a 0%,#3b82f6 100%); color:white; border-radius:8px 8px 0 0; font-weight:600; font-size:12px; }
            .res-wrapper { border:1px solid #e5e7eb; border-radius:8px; overflow:hidden; }
            .res-header .res-id-col { min-width:70px; }
            .res-header .res-customer-col { min-width:150px; }
            .res-header .res-dates-col { min-width:120px; }
            .res-header .res-amount-col { min-width:80px; text-align:right; }
            .res-header .res-status-col { min-width:100px; text-align:center; }
            .res-header .res-combo-col { min-width:100px; }
            .res-header .res-room-col { min-width:180px; }
        </style>`;
    },

    // Get status color
    getStatusColor: function(status) {
        const colors = {
            'TENTATIVO': '#f59e0b',
            'RESERVA SIN PAGO': '#ef4444',
            'RESERVA PAGADA': '#10b981',
            'CHECKIN': '#3b82f6',
            'CHECKOUT': '#6b7280',
            'CANCELADO': '#dc2626',
            'NOSHOW': '#7c3aed'
        };
        return colors[status] || '#6b7280';
    },

    // Format currency
    formatCurrency: function(amount) {
        return `Q${parseFloat(amount || 0).toFixed(2)}`;
    },

    // Build room badges HTML
    buildRoomsHtml: function(habitacion) {
        if (!habitacion) {
            return '<span class="res-room" style="background:#e5e7eb; color:#6b7280;">-</span>';
        }
        let html = '';
        habitacion.split(' | ').forEach(function(room) {
            html += `<span class="res-room">${frappe.utils.escape_html(room.trim())}</span> `;
        });
        return html;
    },

    // Build combo badges HTML
    buildComboHtml: function(codigo_combo) {
        if (!codigo_combo) {
            return '<span class="res-combo">-</span>';
        }
        let html = '';
        codigo_combo.split(' | ').forEach(function(combo) {
            if (combo) {
                html += `<span class="res-combo">${frappe.utils.escape_html(combo.trim())}</span> `;
            }
        });
        return html || '<span class="res-combo">-</span>';
    },

    // Build single reservation card HTML
    buildReservationCard: function(res) {
        const self = hermes_reservation_selector;
        const statusColor = self.getStatusColor(res.estado_reserva);
        const roomsHtml = self.buildRoomsHtml(res.habitacion);
        const comboHtml = self.buildComboHtml(res.codigo_combo);
        
        return `<div class="res-card" 
            data-name="${frappe.utils.escape_html(res.name || '')}" 
            data-customer="${frappe.utils.escape_html(res.customer_name || res.cliente || '')}" 
            data-fecha-entrada="${frappe.utils.escape_html(res.fecha_entrada || '')}" 
            data-fecha-salida="${frappe.utils.escape_html(res.fecha_salida || '')}" 
            data-total-global="${frappe.utils.escape_html(res.total_global || '')}" 
            data-total-abonado="${frappe.utils.escape_html(res.total_abonado || '')}" 
            data-estado-reserva="${frappe.utils.escape_html(res.estado_reserva || '')}" 
            data-habitacion="${frappe.utils.escape_html(res.habitacion || '')}" 
            data-codigo-combo="${frappe.utils.escape_html(res.codigo_combo || '')}">
            <div class="res-id-col"><span class="res-id">${frappe.utils.escape_html(res.name || '')}</span></div>
            <div class="res-customer-col"><span class="res-customer">${frappe.utils.escape_html(res.customer_name || res.cliente || '-')}</span></div>
            <div class="res-dates-col">
                <div class="res-date-label">Entrada</div>
                <div class="res-date">${frappe.utils.escape_html(res.fecha_entrada || '-')}</div>
                <div class="res-date-label" style="margin-top:2px">Salida</div>
                <div class="res-date">${frappe.utils.escape_html(res.fecha_salida || '-')}</div>
            </div>
            <div class="res-amount-col">
                <div class="res-amount">${self.formatCurrency(res.total_global)}</div>
                <div class="res-paid">${self.formatCurrency(res.total_abonado)}</div>
            </div>
            <div class="res-status-col"><span class="res-badge" style="background:${statusColor}">${frappe.utils.escape_html(res.estado_reserva || '-')}</span></div>
            <div class="res-combo-col">${comboHtml}</div>
            <div class="res-room-col">${roomsHtml}</div>
        </div>`;
    },

    // Import combo items from reservation
    importCombosFromReservation: async function(frm, codigo_combo_str) {
        const self = hermes_reservation_selector;
        
        // Parse codigo_combo string into array (separated by ' | ')
        if (!codigo_combo_str || codigo_combo_str.trim() === '') {
            console.log('No codigo_combo found in reservation');
            return;
        }
        
        // Create matrix of codigo_combo values (keep duplicates - each combo adds its items)
        const comboCodes = codigo_combo_str.split(' | ')
            .map(c => c.trim())
            .filter(c => c && c !== '-');
        
        console.log('=== COMBO CODES MATRIX ===', comboCodes);
        
        if (comboCodes.length === 0) {
            frappe.show_alert({
                message: __("La reserva no tiene códigos de combo"),
                indicator: "orange"
            });
            return;
        }
        
        // Remove empty rows from items table (rows without item_code)
        frm.doc.items = (frm.doc.items || []).filter(row => row.item_code);
        frm.refresh_field('items');
        
        // Track total items to add for progress
        let totalItemsAdded = 0;
        let currentDelay = 0;
        
        // Process each combo code sequentially (including duplicates)
        for (const comboCode of comboCodes) {
            console.log(`Processing combo: ${comboCode}`);
            
            try {
                // Get Product Bundle items
                const response = await frappe.call({
                    method: 'frappe.client.get',
                    args: {
                        doctype: 'Product Bundle',
                        name: comboCode
                    }
                });
                
                if (!response.message || !response.message.items || response.message.items.length === 0) {
                    console.log(`No items found for combo: ${comboCode}`);
                    continue;
                }
                
                const bundleItems = response.message.items;
                console.log(`Found ${bundleItems.length} items for combo: ${comboCode}`);
                
                // Add each item from the bundle with delay
                for (const bundleItem of bundleItems) {
                    currentDelay += 500; // 500ms delay between each item
                    
                    await new Promise(resolve => {
                        setTimeout(async () => {
                            const child = frm.add_child('items');
                            child.qty = bundleItem.qty;
                            
                            if (frm.doc.set_warehouse) {
                                child.warehouse = frm.doc.set_warehouse;
                            }
                            
                            await frappe.model.set_value(child.doctype, child.name, 'item_code', bundleItem.item_code);
                            frm.refresh_field('items');
                            totalItemsAdded++;
                            resolve();
                        }, currentDelay);
                    });
                }
                
            } catch (err) {
                console.error(`Error processing combo ${comboCode}:`, err);
            }
        }
        
        // Show success message
        if (totalItemsAdded > 0) {
            frappe.show_alert({
                message: __(`Se agregaron ${totalItemsAdded} items de ${comboCodes.length} combo(s)`),
                indicator: "green"
            });
        }
    },

    // Handle reservation card click
    handleReservationClick: async function(frm, $card, dialog) {
        const self = hermes_reservation_selector;
        const codigo_combo = $card.attr('data-codigo-combo');
        
        dialog.hide();
        
        console.log('=== RESERVATION SELECTED ===', { 
            name: $card.attr('data-name'),
            customer: $card.attr('data-customer'),
            habitacion: $card.attr('data-habitacion'),
            codigo_combo: codigo_combo
        });
        
        // Import combo items from reservation
        await self.importCombosFromReservation(frm, codigo_combo);
    },

    // Main function to show reservation selector dialog
    show_dialog: function(frm) {
        const self = hermes_reservation_selector;
        console.log('=== RESERVATION SELECTOR v5.0 (Hermes App) ===');
        
        frappe.call({
            method: "hermes.api.get_recent_reservations",
            args: { limit: 25 },
            callback: function(r) {
                console.log('=== RESERVATIONS DATA ===', r.message);
                
                if (!r.message || r.message.length === 0) {
                    frappe.msgprint(__("No se encontraron reservas."));
                    return;
                }
                
                const reservations = r.message;
                
                // Build HTML
                let html = self.getStyles();
                html += `<div class="res-container">
                    <div class="res-header">
                        <div class="res-id-col">ID</div>
                        <div class="res-customer-col">Cliente</div>
                        <div class="res-dates-col">Fechas</div>
                        <div class="res-amount-col">Valor</div>
                        <div class="res-status-col">Status</div>
                        <div class="res-combo-col">Combo</div>
                        <div class="res-room-col">Habitaciones</div>
                    </div>
                    <div class="res-wrapper">`;
                
                reservations.forEach(res => {
                    html += self.buildReservationCard(res);
                });
                
                html += `</div></div>`;
                
                // Create and show dialog
                const d = new frappe.ui.Dialog({
                    title: __("Seleccionar Reserva"),
                    fields: [{
                        fieldtype: "HTML",
                        fieldname: "reservations_html",
                        options: html
                    }],
                    primary_action: function() {
                        d.hide();
                    }
                });
                
                d.show();
                
                // Add click handler
                setTimeout(function() {
                    d.$wrapper.find('.res-card').on('click', function() {
                        self.handleReservationClick(frm, $(this), d);
                    });
                }, 100);
            }
        });
    }
};
