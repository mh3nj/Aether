"""
Font Awesome icon mapping for Aether
Solid icons only - optimized for dark/light theme
"""

ICON_MAP = {
    # Main navigation
    "dashboard": "\uf015",      # fa-home
    "code_studio": "\uf121",    # fa-code
    "seo_command": "\uf002",    # fa-search
    "schema_social": "\uf0e8",  # fa-share-alt
    "media_studio": "\uf302",   # fa-image
    "link_studio": "\uf0c1",    # fa-link
    "accessibility_hub": "\uf29a", # fa-universal-access
    "performance_lab": "\uf3fd",   # fa-gauge-high
    "security_backup": "\uf3ed",   # fa-shield
    "analytics": "\uf080",      # fa-chart-line
    "batch_ops": "\uf013",      # fa-gear
    "logs": "\uf017",           # fa-clock
    
    # Common actions
    "save": "\uf0c7",           # fa-save
    "undo": "\uf0e2",           # fa-undo
    "redo": "\uf01e",           # fa-redo
    "delete": "\uf2ed",         # fa-trash
    "edit": "\uf044",           # fa-pen
    "add": "\uf067",            # fa-plus
    "close": "\uf00d",          # fa-times
    "settings": "\uf013",       # fa-gear
    "help": "\uf059",           # fa-question-circle
    "info": "\uf05a",           # fa-info-circle
    "warning": "\uf071",        # fa-exclamation-triangle
    "success": "\uf00c",        # fa-check
    "error": "\uf06a",          # fa-exclamation-circle
    
    # Specific tools
    "format": "\uf121",         # fa-code
    "optimize": "\uf185",       # fa-bolt
    "preview": "\uf06e",        # fa-eye
    "export": "\uf019",         # fa-download
    "import": "\uf093",         # fa-upload
    "refresh": "\uf021",        # fa-sync
    "search": "\uf002",         # fa-search
    "filter": "\uf0b0",         # fa-filter
    "scan": "\uf002",           # fa-search
    "fix": "\uf0c7",            # fa-save
    "backup": "\uf187",         # fa-hdd
    "restore": "\uf0e2",        # fa-undo
}

def get_icon(name, size="16px"):
    """Get icon HTML/CSS for a given name"""
    code = ICON_MAP.get(name, "\uf128")  # fa-question as fallback
    return f'<span class="fas" style="font-size: {size};">{code}</span>'
