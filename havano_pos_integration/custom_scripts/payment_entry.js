frappe.listview_settings["Payment Entry"] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Process Payments'), function() {
            let d = new frappe.ui.Dialog({
                title: 'Select Date Range',
                fields: [
                    {
                        label: 'Start Date',
                        fieldname: 'start_date',
                        fieldtype: 'Date',
                        reqd: 1,
                        default: frappe.datetime.get_today()
                    },
                    {
                        label: 'End Date',
                        fieldname: 'end_date',
                        fieldtype: 'Date',
                        reqd: 1,
                        default: frappe.datetime.get_today()
                    }
                ],
                primary_action_label: 'Process',
                primary_action(values) {
                    // Create and show the round loader
                    let loader = `
                        <div class="progress-chart">
                            <div class="progress">
                                <div class="progress-bar progress-bar-animated progress-bar-striped" 
                                    role="progressbar" 
                                    style="width: 100%">
                                </div>
                            </div>
                        </div>
                    `;
                    
                    frappe.msgprint({
                        title: __('Processing Payments'),
                        message: loader,
                        indicator: 'blue',
                        wide: true
                    });
                    
                    frappe.call({
                        method: 'havano_pos_integration.update_payment.reprocess_payment_entries',
                        freeze: true,
                        args: {
                            start_date: values.start_date,
                            end_date: values.end_date
                        },
                        callback: function(r) {
                            // Close the loader dialog
                            cur_dialog.hide();
                            frappe.show_alert({
                                message: __(r.message),
                                indicator: 'green'
                            }, 5);
                            listview.refresh();
                        },
                        error: function(r) {
                            cur_dialog.hide();
                            frappe.throw(__('Error processing payments'));
                        }
                    });
                    d.hide();
                }
            });
            d.show();
        });
    }
};