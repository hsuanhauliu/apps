import os
import html

# ---------------------------------------------------------------------------
# Presentation metadata
# ---------------------------------------------------------------------------
# Per-category theming: label, accent colour, soft tint for the icon badge, and
# an inline SVG icon (lucide-style, 24x24, stroke = currentColor). Any category
# that isn't listed here falls back to DEFAULT_CATEGORY so newly-added folders
# still render cleanly.
CATEGORY_META = {
    "art": {
        "label": "Art",
        "accent": "#8b5cf6",
        "tint": "#f5f3ff",
        "icon": '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
    },
    "edit": {
        "label": "Edit",
        "accent": "#4f46e5",
        "tint": "#eef2ff",
        "icon": '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/>',
    },
    "exercise": {
        "label": "Exercise",
        "accent": "#059669",
        "tint": "#ecfdf5",
        "icon": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    },
    "games": {
        "label": "Games",
        "accent": "#ea580c",
        "tint": "#fff7ed",
        "icon": '<line x1="6" x2="10" y1="12" y2="12"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="15" x2="15.01" y1="13" y2="13"/><line x1="18" x2="18.01" y1="11" y2="11"/><rect width="20" height="12" x="2" y="6" rx="2"/>',
    },
    "media": {
        "label": "Media",
        "accent": "#e11d48",
        "tint": "#fff1f2",
        "icon": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
    },
}
DEFAULT_CATEGORY = {
    "label": "Apps",
    "accent": "#475569",
    "tint": "#f1f5f9",
    "icon": '<rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/>',
}

# Short descriptions keyed by the app's relative URL. Missing entries get a
# sensible generic fallback so the page never looks broken.
APP_DESCRIPTIONS = {
    "art/constellation_creator.html": "Drop stars onto a night sky and link them into your own constellations.",
    "art/sketchpad.html": "A clean freehand drawing canvas with adjustable brush and colours.",
    "edit/notebook_editor.html": "A lightweight notebook for jotting, editing and organising notes.",
    "edit/simple_pdf_editor.html": "Edit, merge, reorder, sign and export PDF pages — entirely in your browser.",
    "exercise/stopwatch_timer.html": "A precise stopwatch and countdown timer built for workouts.",
    "exercise/weighted_calisthenics_calculator.html": "Work out your effective training load for weighted calisthenics.",
    "games/blackjack.html": "Play a quick hand of classic blackjack against the dealer.",
    "games/chess_timer.html": "A dual-player chess clock with configurable time controls.",
    "games/chessboard_simulation.html": "Set up positions and move pieces on an interactive chessboard.",
    "games/ping_pong_scorer.html": "Keep score for table-tennis matches, with landscape support.",
    "games/tetris.html": "The timeless falling-blocks puzzle, playable in the browser.",
    "media/image_metadata_remover.html": "Strip EXIF and hidden metadata from images, locally and privately.",
    "media/qr_generator.html": "Generate crisp QR codes from any text or link in seconds.",
}

# Prettify acronyms that .title() would otherwise mangle.
TITLE_FIXUPS = {"Pdf": "PDF", "Qr": "QR", "Exif": "EXIF"}


def prettify_title(filename):
    name = filename[:-5] if filename.endswith(".html") else filename
    title = name.replace("_", " ").title()
    for wrong, right in TITLE_FIXUPS.items():
        title = title.replace(wrong, right)
    return title


def generate_mobile_links_page(target_folder="docs", output_filename="index.html"):
    target_path = os.path.join(os.getcwd(), target_folder)
    output_path = os.path.join(target_path, output_filename)

    if not os.path.isdir(target_path):
        print(f"🛑 Error: Target folder '{target_folder}' not found.")
        return

    print(f"Scanning for .html files inside '{target_folder}'...")
    apps = []
    for root, _, files in os.walk(target_path):
        relative_root = os.path.relpath(root, target_path).replace(os.path.sep, "/")
        for file in files:
            if not file.endswith(".html"):
                continue
            if relative_root == "." and file == output_filename:
                continue

            if relative_root == ".":
                url = file
                category = "root"
            else:
                url = f"{relative_root}/{file}"
                category = relative_root.split("/")[0]

            apps.append({
                "url": url,
                "category": category,
                "title": prettify_title(file),
                "description": APP_DESCRIPTIONS.get(url, "Open this single-page web app."),
            })

    apps.sort(key=lambda a: (a["category"].lower(), a["title"].lower()))
    print(f"Found {len(apps)} linkable pages.")

    # Categories present, ordered by their card count (desc) then name.
    counts = {}
    for a in apps:
        counts[a["category"]] = counts.get(a["category"], 0) + 1
    ordered_categories = sorted(counts, key=lambda c: (-counts[c], c))

    def cat_meta(cat):
        return CATEGORY_META.get(cat, DEFAULT_CATEGORY)

    # --- Filter pills ---
    pills = [f'<button class="pill is-active" data-filter="all">All'
             f'<span class="pill-count">{len(apps)}</span></button>']
    for cat in ordered_categories:
        meta = cat_meta(cat)
        pills.append(
            f'<button class="pill" data-filter="{html.escape(cat)}" '
            f'style="--accent:{meta["accent"]}">'
            f'{html.escape(meta["label"])}'
            f'<span class="pill-count">{counts[cat]}</span></button>'
        )
    pills_html = "\n            ".join(pills)

    # --- Cards ---
    cards = []
    for a in apps:
        meta = cat_meta(a["category"])
        title = html.escape(a["title"])
        desc = html.escape(a["description"])
        label = html.escape(meta["label"])
        search = html.escape(f'{a["title"]} {a["description"]} {meta["label"]}'.lower(), quote=True)
        cards.append(f"""
            <a href="{a['url']}" class="card" data-category="{html.escape(a['category'])}" data-search="{search}"
               style="--accent:{meta['accent']}; --tint:{meta['tint']}">
                <span class="card-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
                         stroke-linecap="round" stroke-linejoin="round">{meta['icon']}</svg>
                </span>
                <span class="card-title">{title}</span>
                <span class="card-desc">{desc}</span>
                <span class="card-foot">
                    <span class="card-tag">{label}</span>
                    <span class="card-open">Open
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                             stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
                    </span>
                </span>
            </a>""")
    cards_html = "\n".join(cards)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hsuan-Hau Liu · App Gallery</title>
    <meta name="description" content="A collection of small, single-page web apps by Hsuan-Hau Liu — no installs, no accounts.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #f8fafc;
            --surface: #ffffff;
            --ink: #0f172a;
            --muted: #64748b;
            --line: #e7ebf0;
            --ring: rgba(79, 70, 229, .18);
        }}
        * {{ box-sizing: border-box; }}
        html {{ -webkit-text-size-adjust: 100%; }}
        body {{
            margin: 0;
            font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
            color: var(--ink);
            background: var(--bg);
            background-image:
                radial-gradient(60rem 60rem at 110% -10%, #eef2ff 0%, rgba(238,242,255,0) 55%),
                radial-gradient(50rem 50rem at -10% 0%, #f5f3ff 0%, rgba(245,243,255,0) 50%);
            background-attachment: fixed;
            -webkit-font-smoothing: antialiased;
        }}
        .wrap {{ max-width: 1120px; margin: 0 auto; padding: 0 20px 80px; }}

        /* Header */
        header {{ padding: 72px 0 40px; text-align: center; }}
        .eyebrow {{
            display: inline-flex; align-items: center; gap: 8px;
            font-size: 13px; font-weight: 600; letter-spacing: .02em;
            color: var(--muted); background: var(--surface);
            border: 1px solid var(--line); padding: 6px 14px; border-radius: 999px;
            box-shadow: 0 1px 2px rgba(15,23,42,.04);
        }}
        .eyebrow .dot {{ width: 7px; height: 7px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 0 3px rgba(34,197,94,.18); }}
        h1 {{
            margin: 22px 0 0; font-size: clamp(2rem, 5vw, 3.15rem); font-weight: 800;
            letter-spacing: -0.03em; line-height: 1.05;
        }}
        h1 .grad {{
            background: linear-gradient(100deg, #4f46e5, #8b5cf6 55%, #e11d48);
            -webkit-background-clip: text; background-clip: text; color: transparent;
        }}
        .lede {{
            margin: 16px auto 0; max-width: 560px; color: var(--muted);
            font-size: 1.05rem; line-height: 1.6;
        }}

        /* Controls */
        .controls {{
            position: sticky; top: 0; z-index: 20;
            display: flex; flex-direction: column; gap: 14px; align-items: center;
            padding: 16px 0; margin-bottom: 8px;
            background: linear-gradient(var(--bg) 62%, rgba(248,250,252,0));
        }}
        .search {{
            position: relative; width: 100%; max-width: 440px;
        }}
        .search svg {{
            position: absolute; left: 15px; top: 50%; transform: translateY(-50%);
            width: 18px; height: 18px; color: var(--muted); pointer-events: none;
        }}
        .search input {{
            width: 100%; padding: 13px 16px 13px 44px; font-size: 15px; font-family: inherit;
            color: var(--ink); background: var(--surface);
            border: 1px solid var(--line); border-radius: 12px; outline: none;
            box-shadow: 0 1px 2px rgba(15,23,42,.04); transition: border-color .15s, box-shadow .15s;
        }}
        .search input::placeholder {{ color: #94a3b8; }}
        .search input:focus {{ border-color: #c7cbff; box-shadow: 0 0 0 4px var(--ring); }}

        .pills {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }}
        .pill {{
            --accent: #4f46e5;
            display: inline-flex; align-items: center; gap: 8px;
            font: inherit; font-size: 13.5px; font-weight: 600; color: var(--muted);
            background: var(--surface); border: 1px solid var(--line);
            padding: 8px 14px; border-radius: 999px; cursor: pointer;
            transition: color .15s, border-color .15s, background .15s, transform .1s;
        }}
        .pill:hover {{ color: var(--ink); border-color: #cbd5e1; }}
        .pill:active {{ transform: translateY(1px); }}
        .pill .pill-count {{
            font-size: 12px; font-weight: 700; color: var(--muted);
            background: #f1f5f9; border-radius: 999px; padding: 1px 8px; min-width: 22px; text-align: center;
        }}
        .pill.is-active {{
            color: #fff; background: var(--accent); border-color: var(--accent);
            box-shadow: 0 6px 16px -6px var(--accent);
        }}
        .pill.is-active .pill-count {{ color: #fff; background: rgba(255,255,255,.22); }}

        /* Grid */
        .grid {{
            display: grid; gap: 18px;
            grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
        }}
        .card {{
            position: relative; display: flex; flex-direction: column;
            padding: 22px; border-radius: 18px; text-decoration: none;
            color: inherit; background: var(--surface); border: 1px solid var(--line);
            box-shadow: 0 1px 2px rgba(15,23,42,.04);
            transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
            overflow: hidden;
        }}
        .card::before {{
            content: ""; position: absolute; inset: 0 0 auto 0; height: 3px;
            background: var(--accent); opacity: 0; transition: opacity .16s ease;
        }}
        .card:hover {{
            transform: translateY(-4px);
            border-color: color-mix(in srgb, var(--accent) 35%, var(--line));
            box-shadow: 0 18px 40px -18px color-mix(in srgb, var(--accent) 55%, transparent);
        }}
        .card:hover::before {{ opacity: 1; }}
        .card-icon {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 46px; height: 46px; border-radius: 13px;
            background: var(--tint); color: var(--accent); margin-bottom: 16px;
        }}
        .card-icon svg {{ width: 24px; height: 24px; }}
        .card-title {{ font-size: 1.12rem; font-weight: 700; letter-spacing: -0.01em; }}
        .card-desc {{ margin-top: 6px; color: var(--muted); font-size: .92rem; line-height: 1.5; flex: 1; }}
        .card-foot {{
            display: flex; align-items: center; justify-content: space-between;
            margin-top: 18px;
        }}
        .card-tag {{
            font-size: 12px; font-weight: 600; color: var(--accent);
            background: var(--tint); padding: 4px 10px; border-radius: 999px;
        }}
        .card-open {{
            display: inline-flex; align-items: center; gap: 5px;
            font-size: 13px; font-weight: 600; color: var(--muted);
            transition: gap .16s ease, color .16s ease;
        }}
        .card-open svg {{ width: 15px; height: 15px; }}
        .card:hover .card-open {{ color: var(--accent); gap: 9px; }}

        .empty {{
            display: none; text-align: center; padding: 60px 20px; color: var(--muted);
        }}
        .empty.show {{ display: block; }}
        .empty strong {{ display: block; color: var(--ink); font-size: 1.1rem; margin-bottom: 4px; }}

        footer {{
            margin-top: 56px; text-align: center; color: #94a3b8; font-size: 13px;
        }}
        footer a {{ color: var(--muted); text-decoration: none; border-bottom: 1px solid var(--line); }}
        footer a:hover {{ color: var(--ink); }}

        @media (max-width: 560px) {{
            header {{ padding: 48px 0 28px; }}
            .grid {{ grid-template-columns: 1fr; }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            * {{ transition: none !important; }}
        }}
    </style>
</head>
<body>
    <div class="wrap">
        <header>
            <span class="eyebrow"><span class="dot"></span>Hsuan-Hau Liu · Client Apps</span>
            <h1>A little gallery of<br><span class="grad">handy web apps</span></h1>
            <p class="lede">Small, fast, single-page tools that run entirely in your browser — no installs, no sign-ups, nothing leaves your device.</p>
        </header>

        <div class="controls">
            <label class="search">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
                <input id="search" type="search" placeholder="Search apps…" autocomplete="off" aria-label="Search apps">
            </label>
            <div class="pills" id="pills">
            {pills_html}
            </div>
        </div>

        <main class="grid" id="grid">{cards_html}
        </main>

        <div class="empty" id="empty">
            <strong>No apps found</strong>
            Try a different search or category.
        </div>

        <footer>
            Built with plain HTML, CSS &amp; JavaScript · {len(apps)} apps
        </footer>
    </div>

    <script>
        (function () {{
            const grid = document.getElementById('grid');
            const cards = Array.from(grid.querySelectorAll('.card'));
            const pills = Array.from(document.querySelectorAll('.pill'));
            const search = document.getElementById('search');
            const empty = document.getElementById('empty');
            let activeFilter = 'all';

            function apply() {{
                const q = search.value.trim().toLowerCase();
                let visible = 0;
                cards.forEach(card => {{
                    const matchesCat = activeFilter === 'all' || card.dataset.category === activeFilter;
                    const matchesText = !q || card.dataset.search.includes(q);
                    const show = matchesCat && matchesText;
                    card.style.display = show ? '' : 'none';
                    if (show) visible++;
                }});
                empty.classList.toggle('show', visible === 0);
            }}

            pills.forEach(pill => pill.addEventListener('click', () => {{
                pills.forEach(p => p.classList.remove('is-active'));
                pill.classList.add('is-active');
                activeFilter = pill.dataset.filter;
                apply();
            }}));

            search.addEventListener('input', apply);
        }})();
    </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ Successfully generated {output_filename} inside '{target_folder}'.")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    generate_mobile_links_page(target_folder="docs")
