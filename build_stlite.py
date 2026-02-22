import os
import json

def generate_stlite_index():
    # Base configuration for Stlite
    stlite_config = {
        "requirements": ["streamlit", "pandas", "requests", "beautifulsoup4", "textblob"],
        "entrypoint": "app.py",
        "files": {}
    }

    # Files to include
    include_extensions = ['.py', '.json', '.md', '.png', '.jpg', '.jpeg', '.gif']
    exclude_dirs = ['venv', '__pycache__', '.git', '.vscode', '.idea']
    
    # Walk through the directory
    for root, dirs, files in os.walk('.'):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            # Check extension
            if not any(file.endswith(ext) for ext in include_extensions):
                continue
                
            # Get relative path
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, '.')
            
            # Normalize path separators to forward slashes
            rel_path = rel_path.replace('\\', '/')
            
            # Skip build script itself and hidden files
            if rel_path == 'build_stlite.py' or file.startswith('.'):
                continue

            # Add to files configuration
            # For Vercel, we can just point to the URL since it serves static files
            stlite_config['files'][rel_path] = {
                "url": rel_path
            }

    # Generate HTML content
    html_content = f"""<!doctype html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>US School Research Assistant</title>
    <link rel="icon" href="favicon.png" type="image/png">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.53.0/build/stlite.css">
  </head>
  <body>
    <div id="root"></div>
    <script src="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.53.0/build/stlite.js"></script>
    <script>
      stlite.mount({json.dumps(stlite_config, indent=2)}, document.getElementById("root"))
    </script>
  </body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated index.html with {len(stlite_config['files'])} files.")

if __name__ == "__main__":
    generate_stlite_index()
