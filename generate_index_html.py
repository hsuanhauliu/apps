import os

def generate_mobile_links_page(target_folder="my_website", output_filename="index.html"):
    # ... (Keep existing setup and error handling) ...

    target_path = os.path.join(os.getcwd(), target_folder)
    output_path = os.path.join(target_path, output_filename)
    
    if not os.path.isdir(target_path):
        print(f"🛑 Error: Target folder '{target_folder}' not found.")
        return

    links = []
    unique_dirs = set() # NEW: Set to store unique directories
    
    print(f"Scanning for .html files inside '{target_folder}'...")
    for root, _, files in os.walk(target_path):
        relative_root = os.path.relpath(root, target_path)
        
        # NEW: Add directory to the set, excluding the root path ('.')
        if relative_root != ".":
             unique_dirs.add(relative_root.replace(os.path.sep, '/'))

        for file in files:
            if file.endswith(".html") and (relative_root != "." or file != output_filename):
                
                if relative_root == ".":
                    relative_url = file
                else:
                    relative_url = os.path.join(relative_root, file).replace(os.path.sep, '/')
                
                file_name_display = file.replace(".html", "").replace("_", " ").title()
                
                # --- Naming for Display ---
                if relative_root == ".":
                    button_name = file_name_display
                    # NEW: Store directory info in the link list for later use in button data attributes
                    directory_class = "root-dir"
                else:
                    dir_path_display = relative_root.replace(os.path.sep, '/') + "/"
                    button_name = f"{file_name_display} <span class='directory'>({dir_path_display})</span>"
                    # NEW
                    directory_class = relative_root.replace(os.path.sep, '/')

                # Tuple format: (Sort Key 1: Directory, Sort Key 2: File Name, Link Data)
                # UPDATED: Added directory_class for use in HTML
                links.append((relative_root, file_name_display, relative_url, button_name, directory_class))
    
    # ... (Keep sorting logic, but adjust lambda if necessary, though it looks fine) ...
    # Current tuple is (rel_root, file_name_display, rel_url, button_name, directory_class) - length 5
    links.sort(key=lambda x: (
        0 if x[0] == "." else 1,    # Key 1: Root folder first (0), others (1)
        x[0].lower(),               # Key 2: Directory name alphabetically
        x[1].lower()                # Key 3: File name alphabetically
    ))
    
    print(f"Found {len(links)} linkable pages.")

    # 1. Generate HTML options for the filter dropdown
    directory_options = ['<option value="all" selected>All Directories</option>']
    # Sort the unique directories alphabetically
    sorted_dirs = sorted(list(unique_dirs), key=str.lower)

    for dir_path in sorted_dirs:
        # Use the full path as the value
        directory_options.append(f'<option value="{dir_path}">{dir_path}/</option>')

    filter_options_html = "\n".join(directory_options)

    # 2. Generate HTML link buttons
    link_html = []
    button_classes = ["primary-btn", "secondary-btn"] 
    
    # Unpack the sorted links, using the new directory_class (index 4)
    # x[2] = url, x[3] = name, x[4] = directory_class
    for i, (_, _, url, name, directory_class) in enumerate(links):
        class_name = button_classes[i % len(button_classes)]
        
        # UPDATED: Add a data attribute for filtering
        link_html.append(f"""
        <a href="{url}" class="link-button {class_name}" data-directory="{directory_class}">
            {name}
        </a>
        """)

    links_block = "\n".join(link_html)

    # 3. Assemble the final HTML page (UPDATED: CSS, Filter HTML, and JS added)
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hsuan-Hau Liu Client Apps</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #1e1e1e;
            color: #f0f0f0;
            text-align: center;
        }}
        .header-container {{
            max-width: 450px;
            margin: 0 auto 20px auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
            text-align: left;
        }}
        .filter-select {{ /* NEW */
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #333;
            background-color: #2a2a2a;
            color: #f0f0f0;
            font-size: 1em;
            width: 100%;
            box-sizing: border-box;
            -webkit-appearance: none; /* Remove default styling on mobile */
            -moz-appearance: none;
            appearance: none;
            cursor: pointer;
        }}
        .link-container {{
            display: flex;
            flex-direction: column;
            gap: 15px;
            max-width: 450px;
            margin: 0 auto;
        }}
        .link-button {{
            display: block;
            padding: 18px 20px;
            color: #f0f0f0;
            text-decoration: none;
            border-radius: 6px;
            font-size: 1.15em;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
            transition: background-color 0.2s ease, transform 0.1s ease, opacity 0.3s; /* Added opacity */
            text-align: left;
        }}
        
        /* Hidden state for filtering */
        .link-button.hidden {{ /* NEW */
            display: none;
            opacity: 0;
        }}
        
        /* Directory path styling (softer look) */
        .link-button .directory {{
            font-weight: normal;
            color: #bbbbbb;
            font-size: 0.9em;
            display: block;
            margin-top: 5px;
        }}

        /* Primary Button Color (Soothing Blue/Green) */
        .primary-btn {{
            background-color: #3f51b5;
        }}
        .primary-btn:hover {{
            background-color: #303f9f;
        }}

        /* Secondary Button Color (Alternating contrast) */
        .secondary-btn {{
            background-color: #009688;
        }}
        .secondary-btn:hover {{
            background-color: #00796b;
        }}
        
        .link-button:active {{
            transform: translateY(1px);
        }}
        
        p {{
            color: #999;
        }}
    </style>
</head>
<body>

    <div class="header-container">
        <select id="directoryFilter" class="filter-select">
            {filter_options_html}
        </select>
    </div>

    <div class="link-container" id="linkContainer">
        {links_block}
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const filter = document.getElementById('directoryFilter');
            const links = document.querySelectorAll('.link-button');

            filter.addEventListener('change', (event) => {{
                const selectedDir = event.target.value;

                links.forEach(link => {{
                    const linkDir = link.getAttribute('data-directory');

                    if (selectedDir === 'all') {{
                        link.classList.remove('hidden');
                    }} else if (linkDir === selectedDir || (selectedDir === 'root-dir' && linkDir === 'root-dir')) {{
                        // 'root-dir' is the value for files directly in the target folder
                        link.classList.remove('hidden');
                    }} else {{
                        link.classList.add('hidden');
                    }}
                }});
            }});
        }});
    </script>

</body>
</html>
"""

    # 4. Write the content to the file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ Successfully generated {output_filename} inside '{target_folder}'.")
    print(f"Output file: {output_path}")

if __name__ == "__main__":
    generate_mobile_links_page(target_folder="docs")
