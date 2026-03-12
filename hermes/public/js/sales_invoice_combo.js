// Copyright (c) 2025, aet and contributors
// License: GNU General Public License v3. See license.txt

/**
 * Simplified Product Bundle functionality for Sales Invoice
 * When user selects a "codigo_combo" in the header, automatically adds bundle items to the invoice
 */

frappe.ui.form.on('Sales Invoice', {
    codigo_combo: function(frm) {
        if (!frm.doc.codigo_combo) return;

        let combo_code = frm.doc.codigo_combo;

        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Product Bundle',
                name: combo_code
            },
            callback: function(r) {
                if (!r.message || !r.message.items || r.message.items.length === 0) return;

                // Remove empty rows from items table
                frm.doc.items = (frm.doc.items || []).filter(row => row.item_code);
                frm.refresh_field('items');

                // Add each item from the bundle
                r.message.items.forEach(function(bundle_item, index) {
                    let child = frm.add_child('items');
                    child.qty = bundle_item.qty;

                    if (frm.doc.set_warehouse) {
                        child.warehouse = frm.doc.set_warehouse;
                    }

                    // Trigger item_code change event with delay to ensure each row is processed separately
                    // Using 500ms delay between each item to prevent race conditions
                    let delay = 500 * (index + 1);
                    setTimeout(function() {
                        frappe.model.set_value(child.doctype, child.name, 'item_code', bundle_item.item_code);
                        frm.refresh_field('items');
                    }, delay);
                });

                frm.refresh_field('items');

                // Note: The codigo_combo field is NOT cleared automatically
                // User can manually clear it when needed
            }
        });
    }
});
