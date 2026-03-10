import frappe

def get_context(context):
    """Serve the Hermes PWA - no cache for development"""
    context.title = "Hermes"
    context.no_cache = 1
    context.bootstrap = 0  # Don't load Frappe's bootstrap
    context.jinja = 0  # Don't wrap in Frappe's template
    return context
