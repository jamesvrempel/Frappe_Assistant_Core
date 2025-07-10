frappe.pages['assistant-admin'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Assistant MCP Admin',
        single_column: true
    });

    page.main.html(`
        <div class="frappe-card">
            <div class="frappe-card-head">
                <strong>MCP API Status</strong>
            </div>
            <div class="frappe-card-body">
                <div id="status-display" class="text-muted">Loading...</div>
                <button class="btn btn-primary btn-sm" id="refresh-status">Refresh Status</button>
            </div>
        </div>
        
        <div class="frappe-card">
            <div class="frappe-card-head">
                <strong>Configuration</strong>
            </div>
            <div class="frappe-card-body">
                <button class="btn btn-primary btn-sm" id="open-settings">Open Settings</button>
                <p class="text-muted mt-2">
                    <small>Enable/disable MCP API access in the settings. The API uses Frappe's web server - no separate server process required.</small>
                </p>
            </div>
        </div>
        
        <div class="frappe-card">
            <div class="frappe-card-head">
                <strong>Usage Statistics</strong>
            </div>
            <div class="frappe-card-body">
                <div id="usage-stats" class="text-muted">Loading...</div>
                <button class="btn btn-secondary btn-sm" id="refresh-stats">Refresh Stats</button>
                <button class="btn btn-warning btn-sm" id="test-logging">Test Logging</button>
            </div>
        </div>
        
        <div class="frappe-card">
            <div class="frappe-card-head">
                <strong>MCP Endpoints</strong>
            </div>
            <div class="frappe-card-body">
                <p><strong>API Endpoint:</strong> <code>/api/method/frappe_assistant_core.api.assistant_api.handle_assistant_request</code></p>
                <p><strong>Ping Endpoint:</strong> <code>/api/method/frappe_assistant_core.api.assistant_api.ping</code></p>
                <button class="btn btn-secondary btn-sm" id="test-ping">Test Ping</button>
            </div>
        </div>
    `);

    // Load server status
    function loadServerStatus() {
        frappe.call({
            method: "frappe_assistant_core.assistant_core.server.get_server_status",
            callback: function(response) {
                if (response.message) {
                    const status = response.message;
                    const statusDisplay = page.main.find('#status-display');
                    const statusText = status.enabled ? 
                        `<span class="text-success">Enabled</span> - MCP API endpoints are active` :
                        `<span class="text-danger">Disabled</span> - MCP API endpoints are inactive`;
                    statusDisplay.html(statusText);
                }
            }
        });
    }

    // Load usage statistics
    function loadUsageStats() {
        frappe.call({
            method: "frappe_assistant_core.api.assistant_api.get_usage_statistics",
            callback: function(response) {
                if (response.message && response.message.success) {
                    const stats = response.message.data;
                    const statsDisplay = page.main.find('#usage-stats');
                    
                    const statsHTML = `
                        <div class="row">
                            <div class="col-md-4">
                                <h6>Connections</h6>
                                <p>Total: <strong>${stats.connections.total}</strong></p>
                                <p>Today: <strong>${stats.connections.today}</strong></p>
                                <p>This Week: <strong>${stats.connections.this_week}</strong></p>
                            </div>
                            <div class="col-md-4">
                                <h6>Audit Logs</h6>
                                <p>Total: <strong>${stats.audit_logs.total}</strong></p>
                                <p>Today: <strong>${stats.audit_logs.today}</strong></p>
                                <p>This Week: <strong>${stats.audit_logs.this_week}</strong></p>
                            </div>
                            <div class="col-md-4">
                                <h6>Tools</h6>
                                <p>Total: <strong>${stats.tools.total}</strong></p>
                                <p>Enabled: <strong>${stats.tools.enabled}</strong></p>
                            </div>
                        </div>
                        ${stats.recent_activity.length > 0 ? `
                        <h6 class="mt-3">Recent Activity</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr><th>Action</th><th>Tool</th><th>User</th><th>Status</th><th>Time</th></tr>
                                </thead>
                                <tbody>
                                    ${stats.recent_activity.map(activity => `
                                        <tr>
                                            <td>${activity.action}</td>
                                            <td>${activity.tool_name || '-'}</td>
                                            <td>${activity.user}</td>
                                            <td><span class="badge badge-${activity.status === 'Success' ? 'success' : 'danger'}">${activity.status}</span></td>
                                            <td>${frappe.datetime.str_to_user(activity.timestamp)}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                        ` : '<p class="text-muted mt-3">No recent activity</p>'}
                    `;
                    
                    statsDisplay.html(statsHTML);
                } else {
                    page.main.find('#usage-stats').html('<span class="text-danger">Failed to load statistics</span>');
                }
            }
        });
    }

    // Event handlers
    page.main.find('#refresh-status').on('click', function() {
        loadServerStatus();
    });

    page.main.find('#refresh-stats').on('click', function() {
        loadUsageStats();
    });

    page.main.find('#test-logging').on('click', function() {
        frappe.call({
            method: "frappe_assistant_core.api.assistant_api.force_test_logging",
            callback: function(response) {
                if (response.message && response.message.success) {
                    frappe.show_alert({
                        message: response.message.message,
                        indicator: 'green'
                    });
                    loadUsageStats(); // Refresh stats after creating test logs
                } else {
                    frappe.show_alert({
                        message: response.message ? response.message.message : "Failed to create test logs",
                        indicator: 'red'
                    });
                }
            }
        });
    });


    page.main.find('#open-settings').on('click', function() {
        frappe.set_route('Form', 'Assistant Core Settings');
    });

    page.main.find('#test-ping').on('click', function() {
        frappe.call({
            method: "frappe_assistant_core.api.assistant_api.ping",
            callback: function(response) {
                if (response.message) {
                    frappe.show_alert({
                        message: "Ping successful: " + response.message.message,
                        indicator: 'green'
                    });
                } else {
                    frappe.show_alert({
                        message: "Ping failed",
                        indicator: 'red'
                    });
                }
            }
        });
    });

    // Initial load
    loadServerStatus();
    loadUsageStats();
};