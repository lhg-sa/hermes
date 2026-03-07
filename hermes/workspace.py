import frappe

def create_hermes_workspace():
    """Create Hermes workspace for ERPNext v16."""
    try:
        # Check if workspace already exists
        if frappe.db.exists("Workspace", "Hermes"):
            frappe.msgprint("Workspace 'Hermes' already exists")
            return

        # Create new workspace
        workspace = frappe.new_doc("Workspace")
        workspace.title = "Hermes"
        workspace.label = "Hermes"
        workspace.public = 1
        workspace.module = "Custom"  # Using Custom module since it's a new workspace
        workspace.icon = "rocket"  # You can change this to any icon you prefer
        workspace.indicator_color = "blue"  # You can change this color
        workspace.content = "[]"  # Empty content array
        workspace.save()
        
        # Clear cache to ensure it appears
        frappe.cache().delete_key("bootinfo")
        
        frappe.msgprint("Workspace 'Hermes' created successfully")
        
    except Exception as e:
        frappe.log_error(f"Error creating Hermes workspace: {str(e)}")
        frappe.msgprint(f"Error creating workspace: {str(e)}")