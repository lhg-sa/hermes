import frappe
import os
import glob

def get_context(context):
    """Generate context for the Hermes PWA"""
    # Get the base URL for assets
    site_name = frappe.local.site
    assets_prefix = f"/sites/{site_name}/assets/hermes"
    
    # Check if built files exist - in public/hermes folder
    base_path = frappe.get_app_path('hermes', 'public', 'hermes')
    assets_path = os.path.join(base_path, 'assets')
    
    # Find the actual built JS and CSS files (with hash)
    js_files = glob.glob(os.path.join(assets_path, 'index-*.js'))
    css_files = glob.glob(os.path.join(assets_path, 'index-*.css'))
    
    # Set URLs - use placeholder if files don't exist yet
    context.favicon_url = "/hermes/favicon.ico"
    context.manifest_url = "/hermes/manifest.json"
    
    if js_files:
        # Extract just the filename from the full path
        js_filename = os.path.basename(js_files[0])
        context.js_url = f"/assets/hermes/hermes/assets/{js_filename}"
    else:
        context.js_url = "/assets/hermes/hermes/index.js"
        
    if css_files:
        css_filename = os.path.basename(css_files[0])
        context.css_url = f"/assets/hermes/hermes/assets/{css_filename}"
    else:
        context.css_url = "/assets/hermes/hermes/index.css"
    
    context.app_name = "Hermes"
