# ========================
# 🎨 JAZZMIN CONFIG — Cook Service
# ========================

# JAZZMIN_UI_TWEAKS = {
#     "theme": "flatly",            # Bosh tema (Bootstrap varianti)
#     "navbar": "navbar-dark",      # Yuqori panel qoramtir
#     "sidebar": "dark",            # Chap menyu qoramtir
#     "dark_mode_theme": "slate",   # Tungi rejimda ishlatiladigan tema
#     "footer_fixed": True,
#     "actions_sticky_top": True,
# }

JAZZMIN_SETTINGS = {
    # --- Asosiy ma’lumotlar ---
    "site_title": "Cook Admin",
    "site_header": "Cook Management",
    "site_brand": "Cook Service",
    "site_logo_classes": "img-circle shadow-sm",
    "welcome_sign": "Welcome to  Dashboard",
    "copyright": "© 2025 Cook Service. All rights reserved.",
    "index_title": "Cook Service boshqaruv paneli",

    # --- Qidiruv ---
    "search_model": [
        "custom_user.Address",
        "restaurants.Restaurant",
    ],

    # --- User avatar ---
    "user_avatar": 'media/profile_photos/default_user.png',

    # --- Yuqori menyu (header bar) ---
    "topmenu_links": [
        {"name": "Cook Service", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Saytga o‘tish", "url": "/api/docs/", "new_window": True},
        {"app": "products"},
    ],

    # --- User menyusi ---
    "usermenu_links": [
        {"model": "apps.user"},
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin", "new_window": True},
    ],

    # --- Sidebar menyu sozlamalari ---
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": ["sessions", "admin", "contenttypes"],
    "hide_models": ["auth.Group"],
    "order_with_respect_to": ["apps", "auth"],

    # --- Ikonalar ---
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
        "custom_user.CustomUser": "fas fa-user-tie",

        "restaurants.Restaurants": "fas fa-utensils",
        "restaurants.RestaurantBranches": "fas fa-map-marked-alt",

        "custom_user.Card": "fas fa-credit-card",
        "custom_user.Address": "fas fa-map-marker-alt",
        "custom_user.Device": "fas fa-mobile-alt",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    # --- Modal o'rniga popup ishlatish ---
    "related_modal_active": False,

    # --- UI Tweaks ---
    "custom_css": "css/custom_admin.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,

    # --- Forma tartibi ---
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },

    # --- Tema (bootstrap varianti) ---
    "theme": "flatly",
}