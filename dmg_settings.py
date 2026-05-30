import os.path

# Basics
format = 'UDBZ'
size = '400M'
files = ['dist/Vibe-Code-This.app']
symlinks = {'Applications': '/Applications'}
badge_icon = 'images/AppIcon.icns'

# Window layout
window_rect = ((100, 100), (640, 280))
background = 'builtin-arrow'
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False

# Icon layout
icon_locations = {
    'Vibe-Code-This.app': (140, 120),
    'Applications': (500, 120)
}
