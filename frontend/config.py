# ===================================================
# = CSS OPTIONS
# ===================================================

PAGE_ICON = "frontend/logo/logo-3-squared.jpeg"
PAGE_ICON_OLD = "🚑"

# ===================================================
# = CSS OPTIONS
# ===================================================

CSS_STYLE = """
<style>
.main-header {
    text-align: left;
    color: #3232a8;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.stButton > button {
    background: #42a9df;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.stButton > button:hover {
    background: #74c3a4;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}
</style>
"""

CSS_STYLE_OLD1 = """
<style>
.main-header {
    text-align: left;
    color: #3232a8;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.stButton > button {
    background: #32a860;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.stButton > button:hover {
    background: #74c3a4;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}
</style>
"""

CSS_STYLE_OLD2 = """
<style>
.main-header {
    text-align: left;
    color: #2E86AB;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.stButton > button {
    background: #52aa8a;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.stButton > button:hover {
    background: #74c3a4;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}
.home-button > button:hover {
    background: #4fa070;
}
.proceed-button > button:hover {
    background: #53e4ff;
}
</style>
"""



# ===================================================
# = NAVBAR OPTIONS
# ===================================================

NAVBAR_PAGES = ["Home", "Library", "Tutorials", "Development", "Download"]

NAVBAR_STYLES = {
    "nav": {
        "background-color": "#3232a8",
    },
    "div": {
        "max-width": "32rem",
    },
    "span": {
        "border-radius": "0.5rem",
        "color": "rgb(49, 51, 63)",
        "margin": "0 0.125rem",
        "padding": "0.4375rem 0.625rem",
    },
    "active": {
        "background-color": "rgba(255, 255, 255, 0.25)",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.35)",
    },
}