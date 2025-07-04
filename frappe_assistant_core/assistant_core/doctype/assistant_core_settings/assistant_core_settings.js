// Copyright (c) 2025, Paul Clinton and contributors
// For license information, please see license.txt

frappe.ui.form.on("Assistant Core Settings", {
    refresh(frm) {
        // Add custom buttons
        frm.add_custom_button(__('Refresh Plugins'), function() {
            frappe.call({
                method: 'refresh_plugins',
                doc: frm.doc,
                callback: function(response) {
                    if (!response.exc) {
                        frm.reload_doc();
                    }
                }
            });
        }, __('Actions'));
        
        frm.add_custom_button(__('Refresh Tool Registry'), function() {
            frappe.call({
                method: 'refresh_tool_registry',
                doc: frm.doc,
                callback: function(response) {
                    if (!response.exc) {
                        frappe.msgprint(__('Tool registry updated successfully'));
                    }
                }
            });
        }, __('Actions'));
    }
});

frappe.ui.form.on("Assistant Plugin Config", {
    plugin_name: function(frm, cdt, cdn) {
        // Auto-populate fields when plugin is selected
        let row = locals[cdt][cdn];
        if (row.plugin_name) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Assistant Plugin Repository',
                    name: row.plugin_name
                },
                callback: function(response) {
                    if (response.message) {
                        let plugin = response.message;
                        frappe.model.set_value(cdt, cdn, 'display_name', plugin.display_name);
                        frappe.model.set_value(cdt, cdn, 'description', plugin.description);
                        frappe.model.set_value(cdt, cdn, 'version', plugin.version);
                        frappe.model.set_value(cdt, cdn, 'can_enable', plugin.can_enable);
                        frappe.model.set_value(cdt, cdn, 'validation_error', plugin.validation_error);
                    }
                }
            });
        }
    }
});
