from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3, os

app = Flask(__name__)
app.secret_key = "promptcraft-dev-key"

# ---------------------------------------------------------------------------
# SQLite persistence
# ---------------------------------------------------------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                text      TEXT    NOT NULL,
                label     TEXT    DEFAULT '',
                platform  TEXT    DEFAULT '',
                tags      TEXT    DEFAULT '',
                saved_at  TEXT    NOT NULL
            )
        """)

init_db()


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Prompt Generator
# ---------------------------------------------------------------------------
STYLE_KEYWORDS = {
    "photorealistic": "photorealistic, hyperrealistic, 8k, DSLR, sharp focus",
    "digital_art": "digital art, artstation, trending, vibrant colours",
    "oil_painting": "oil painting, impasto, textured canvas, classical",
    "watercolor": "watercolour, soft edges, wet-on-wet, pastel tones",
    "anime": "anime style, manga, cel shading, clean lines",
    "concept_art": "concept art, cinematic, detailed environment, matte painting",
    "pixel_art": "pixel art, 16-bit, retro game style",
    "3d_render": "3D render, octane render, subsurface scattering, ray tracing",
}
LIGHTING_KEYWORDS = {
    "golden_hour": "golden hour lighting, warm tones, long shadows",
    "neon": "neon glow, cyberpunk lighting, colourful reflections",
    "studio": "studio lighting, softbox, professional photography",
    "dramatic": "dramatic lighting, chiaroscuro, deep shadows, high contrast",
    "soft": "soft diffused lighting, overcast, gentle shadows",
    "volumetric": "volumetric lighting, god rays, atmospheric haze",
}
PLATFORM_SUFFIX = {
    "midjourney": "--ar {ratio} --v 6 --style raw",
    "dalle": "",
    "stable_diffusion": ", masterpiece, best quality",
    "firefly": "",
    "leonardo": ", ultra detailed, high quality",
}


@app.route("/generator", methods=["GET", "POST"])
def prompt_generator():
    result = None
    idea = platform = style = lighting = ratio = keywords = None

    if request.method == "POST":
        idea      = request.form.get("idea", "").strip()
        platform  = request.form.get("platform", "midjourney")
        style     = request.form.get("style", "")
        lighting  = request.form.get("lighting", "")
        ratio     = request.form.get("ratio", "1:1")
        keywords  = request.form.get("keywords", "").strip()

        parts = [idea]
        if style and style in STYLE_KEYWORDS:
            parts.append(STYLE_KEYWORDS[style])
        if lighting and lighting in LIGHTING_KEYWORDS:
            parts.append(LIGHTING_KEYWORDS[lighting])
        if keywords:
            parts.append(keywords)

        prompt = ", ".join(p for p in parts if p)

        suffix = PLATFORM_SUFFIX.get(platform, "")
        if suffix:
            prompt += " " + suffix.replace("{ratio}", ratio)

        result = prompt

    return render_template("prompt_generator.html",
                           result=result, idea=idea, platform=platform,
                           style=style, lighting=lighting, ratio=ratio,
                           keywords=keywords)


# ---------------------------------------------------------------------------
# Style Explorer
# ---------------------------------------------------------------------------
STYLES = [
    {"name": "Photorealism",      "icon": "fa-camera",        "color": "linear-gradient(135deg,#1a9be6,#1a57e6)",
     "description": "Hyper-detailed photography-style renders.",
     "keywords": "photorealistic, hyperrealistic, 8k, sharp focus, DSLR",
     "tags": "photo real camera"},
    {"name": "Digital Art",       "icon": "fa-desktop",       "color": "linear-gradient(135deg,#e61a9b,#9b1ae6)",
     "description": "Vibrant digital illustrations popular on ArtStation.",
     "keywords": "digital art, artstation, trending, vibrant, detailed",
     "tags": "digital illustration concept"},
    {"name": "Oil Painting",      "icon": "fa-paint-brush",   "color": "linear-gradient(135deg,#e6891a,#e6431a)",
     "description": "Rich classical oil painting textures.",
     "keywords": "oil painting, impasto, textured canvas, classical, old masters",
     "tags": "painting classical traditional"},
    {"name": "Watercolour",       "icon": "fa-droplet",       "color": "linear-gradient(135deg,#1ae6c8,#1a9be6)",
     "description": "Soft, flowing watercolour washes.",
     "keywords": "watercolour, soft edges, wet-on-wet, pastel tones, delicate",
     "tags": "watercolor soft pastel"},
    {"name": "Anime / Manga",     "icon": "fa-star",          "color": "linear-gradient(135deg,#e61a57,#e6a01a)",
     "description": "Japanese animation and manga aesthetics.",
     "keywords": "anime style, manga, cel shading, clean lines, expressive",
     "tags": "anime manga japanese cartoon"},
    {"name": "Concept Art",       "icon": "fa-film",          "color": "linear-gradient(135deg,#1ae657,#1a9be6)",
     "description": "Cinematic matte paintings and world-building art.",
     "keywords": "concept art, cinematic, matte painting, environment design, detailed",
     "tags": "concept cinema matte environment"},
    {"name": "Pixel Art",         "icon": "fa-th",            "color": "linear-gradient(135deg,#e6e61a,#1ae657)",
     "description": "Retro 8-bit and 16-bit pixel aesthetics.",
     "keywords": "pixel art, 16-bit, retro game, sprite, pixelated",
     "tags": "pixel retro game 8bit"},
    {"name": "3D Render",         "icon": "fa-cube",          "color": "linear-gradient(135deg,#9b1ae6,#1a57e6)",
     "description": "Physically-based 3D renders with ray tracing.",
     "keywords": "3D render, octane render, ray tracing, subsurface scattering, PBR",
     "tags": "3d render octane cinema4d"},
    {"name": "Impressionism",     "icon": "fa-sun",           "color": "linear-gradient(135deg,#e6c81a,#e6891a)",
     "description": "Loose brushwork and captured light like Monet.",
     "keywords": "impressionist, loose brushwork, painterly, en plein air, dappled light",
     "tags": "impressionism monet painting light"},
    {"name": "Surrealism",        "icon": "fa-brain",         "color": "linear-gradient(135deg,#c81ae6,#e61a57)",
     "description": "Dream-like impossible imagery inspired by Dalí.",
     "keywords": "surrealist, dreamlike, impossible scene, Dalí inspired, melting",
     "tags": "surreal dream dali bizarre"},
    {"name": "Cyberpunk",         "icon": "fa-robot",         "color": "linear-gradient(135deg,#1ae6e6,#1a1ae6)",
     "description": "Neon-soaked dystopian futures.",
     "keywords": "cyberpunk, neon lights, dystopian, rain-slicked streets, holographic",
     "tags": "cyberpunk neon scifi future"},
    {"name": "Dark Fantasy",      "icon": "fa-dragon",        "color": "linear-gradient(135deg,#3d1a1a,#6b1ae6)",
     "description": "Grim medieval fantasy with dramatic atmosphere.",
     "keywords": "dark fantasy, gothic, dramatic lighting, grimdark, detailed armour",
     "tags": "fantasy dark gothic medieval"},
]


@app.route("/styles")
def style_explorer():
    return render_template("style_explorer.html", styles=STYLES)


# ---------------------------------------------------------------------------
# Prompt Enhancer
# ---------------------------------------------------------------------------
FOCUS_ADDITIONS = {
    "detail":      "intricate details, highly detailed, sharp focus, 8k resolution, fine textures",
    "composition": "rule of thirds, dynamic composition, balanced framing, leading lines, depth of field",
    "lighting":    "dramatic lighting, volumetric rays, cinematic lighting, rim light, atmospheric",
    "style":       "artstation trending, award-winning, masterpiece, professional, polished",
    "technical":   "8k, ultra high resolution, RAW photo, uncompressed, ISO 100, f/2.8",
}
INTENSITY_WRAP = {
    "subtle":   lambda p, add: f"{p}, {add.split(',')[0].strip()}",
    "moderate": lambda p, add: f"{p}, {add}",
    "full":     lambda p, add: f"A breathtaking, {add}, masterfully crafted image of: {p}. Ultra detailed, award-winning.",
}


@app.route("/enhancer", methods=["GET", "POST"])
def prompt_enhancer():
    enhanced = original = None

    if request.method == "POST":
        original  = request.form.get("original", "").strip()
        focus     = request.form.get("focus", "detail")
        platform  = request.form.get("platform", "midjourney")
        intensity = request.form.get("intensity", "moderate")

        additions = FOCUS_ADDITIONS.get(focus, "")
        platform_add = PLATFORM_SUFFIX.get(platform, "")
        wrap = INTENSITY_WRAP.get(intensity, INTENSITY_WRAP["moderate"])
        enhanced = wrap(original, additions)
        if platform_add:
            enhanced += " " + platform_add

    return render_template("prompt_enhancer.html", enhanced=enhanced, original=original)


# ---------------------------------------------------------------------------
# Negative Prompt Builder
# ---------------------------------------------------------------------------
NEGATIVE_MAP = {
    "anatomy":      "bad anatomy, malformed body",
    "hands":        "deformed hands, extra fingers, missing fingers, fused fingers",
    "faces":        "distorted face, asymmetric eyes, crossed eyes, disfigured",
    "blur":         "blurry, out of focus, motion blur, soft",
    "watermark":    "watermark, text, signature, logo, username",
    "artifacts":    "jpeg artifacts, compression artifacts, pixelated",
    "extra_limbs":  "extra limbs, extra arms, extra legs, mutated limbs",
    "mutation":     "mutation, mutated, deformed, ugly",
    "clone":        "duplicate, multiple subjects, cloned faces",
    "lowres":       "low resolution, low quality, worst quality",
    "grainy":       "grainy, noisy, film grain, noise",
    "oversaturated":"oversaturated, overexposed, washed out",
    "cartoon":      "cartoon, animated, childish, flat colours",
    "3d":           "3D render, CGI, plastic, rendered",
    "sketch":       "sketch, draft, unfinished, rough lines",
}


@app.route("/negative", methods=["GET", "POST"])
def negative_prompts():
    result = selected = custom = context = None

    if request.method == "POST":
        selected = request.form.getlist("exclude")
        custom   = request.form.get("custom", "").strip()
        context  = request.form.get("context", "").strip()

        parts = [NEGATIVE_MAP[k] for k in selected if k in NEGATIVE_MAP]
        if custom:
            parts.extend([c.strip() for c in custom.split(",") if c.strip()])

        result = ", ".join(parts)

    return render_template("negative_prompts.html",
                           result=result, selected=selected or [],
                           custom=custom, context=context)


# ---------------------------------------------------------------------------
# Batch Generator
# ---------------------------------------------------------------------------
BATCH_STYLES   = ["photorealistic", "digital art", "oil painting", "watercolour",
                  "anime style", "concept art", "3D render", "impressionist"]
BATCH_LIGHTING = ["golden hour", "neon glow", "studio lighting",
                  "dramatic chiaroscuro", "soft diffused light", "volumetric rays"]
BATCH_MOODS    = ["mysterious", "joyful", "melancholic", "epic", "serene", "eerie"]
BATCH_CAMERAS  = ["wide angle shot", "close-up portrait", "bird's eye view",
                  "low angle shot", "Dutch angle", "macro lens"]
BATCH_TIMES    = ["dawn", "midday", "golden hour", "dusk", "night", "blue hour"]


@app.route("/batch", methods=["GET", "POST"])
def batch_generator():
    results = []
    idea = count = None

    if request.method == "POST":
        idea    = request.form.get("idea", "").strip()
        count   = int(request.form.get("count", 3))
        vary    = request.form.getlist("vary")
        platform = request.form.get("platform", "midjourney")

        import random
        for _ in range(count):
            parts = [idea]
            if "style"    in vary: parts.append(random.choice(BATCH_STYLES))
            if "lighting" in vary: parts.append(random.choice(BATCH_LIGHTING))
            if "mood"     in vary: parts.append(random.choice(BATCH_MOODS))
            if "camera"   in vary: parts.append(random.choice(BATCH_CAMERAS))
            if "time"     in vary: parts.append(random.choice(BATCH_TIMES))
            parts.append("highly detailed, masterpiece")
            results.append(", ".join(parts))

    return render_template("batch_generator.html", results=results, idea=idea, count=count)


# ---------------------------------------------------------------------------
# Prompt Library
# ---------------------------------------------------------------------------
@app.route("/library", methods=["GET", "POST"])
def prompt_library():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "save":
            text = request.form.get("prompt_text", "").strip()
            if text:
                with get_db() as conn:
                    conn.execute(
                        "INSERT INTO prompts (text, label, platform, tags, saved_at) VALUES (?,?,?,?,?)",
                        (
                            text,
                            request.form.get("label", "").strip(),
                            request.form.get("platform", ""),
                            request.form.get("tags", "").strip(),
                            datetime.now().strftime("%d %b %Y %H:%M"),
                        ),
                    )

        elif action == "delete":
            pid = request.form.get("prompt_id", type=int)
            if pid is not None:
                with get_db() as conn:
                    conn.execute("DELETE FROM prompts WHERE id = ?", (pid,))

        return redirect(url_for("prompt_library"))

    with get_db() as conn:
        prompts = conn.execute("SELECT * FROM prompts ORDER BY id DESC").fetchall()

    return render_template("prompt_library.html", prompts=prompts)


# ---------------------------------------------------------------------------
# Template Builder
# ---------------------------------------------------------------------------
@app.route("/template-builder")
def template_builder():
    return render_template("template_builder.html")


@app.route("/template-builder/save", methods=["POST"])
def template_builder_save():
    text = request.form.get("prompt_text", "").strip()
    if text:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO prompts (text, label, platform, tags, saved_at) VALUES (?,?,?,?,?)",
                (
                    text,
                    request.form.get("label", "").strip(),
                    request.form.get("platform", "template"),
                    request.form.get("tags", "template-builder"),
                    datetime.now().strftime("%d %b %Y %H:%M"),
                ),
            )
        flash("Prompt saved to library.", "success")
    else:
        flash("Nothing to save — fill in at least one parameter.", "error")
    return redirect(url_for("template_builder"))


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
