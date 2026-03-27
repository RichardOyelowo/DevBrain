import os
import shutil
from jinja2 import Environment, FileSystemLoader

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
OUTPUT_DIR = os.path.join(BASE_DIR, "frontend_build")

API_SUBDOMAIN = "https://devbrain.com"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Setup Jinja
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

# --- Fake Flask functions ---

def fake_url_for(endpoint, **kwargs):
    if endpoint == "static":
        filename = kwargs.get("filename", "")
        return f"/static/{filename}"
    
    return API_SUBDOMAIN + "/" + endpoint.split(".")[-1]

def fake_get_flashed_messages(*args, **kwargs):
    return []  # no flash messages in static build

# --- Fake Flask globals ---
env.globals.update({
    "url_for": fake_url_for,
    "session": {"user_id": None},   # simulate logged-out
    "get_flashed_messages": fake_get_flashed_messages,
    "request": {},
    "g": {}
})

# --- Render templates ---
for template_name in os.listdir(TEMPLATES_DIR):
    if not template_name.endswith(".html"):
        continue

    template = env.get_template(template_name)
    rendered_html = template.render()

    output_path = os.path.join(OUTPUT_DIR, template_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    print(f"Rendered {template_name}")

# --- Copy static files ---
if os.path.exists(STATIC_DIR):
    shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, "static"), dirs_exist_ok=True)

print("\n✅ DONE. No more Flask errors. Deploy frontend_build/")