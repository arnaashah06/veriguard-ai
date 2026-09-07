# build_walkthrough_pdf.py
import os
import subprocess
import html

DESKTOP_DIR = r"C:\Users\pc\Desktop"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
TXT_PATH = r"C:\Users\pc\Desktop\veriguard-ai\walkthrough.txt"
HTML_PATH = r"C:\Users\pc\Desktop\veriguard-ai\walkthrough_pdf.html"
PDF_DEST = os.path.join(DESKTOP_DIR, "VeriGuard_AI_Master_Walkthrough.pdf")

with open(TXT_PATH, "r", encoding="utf-8") as f:
    text_content = f.read()

escaped = html.escape(text_content)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VeriGuard AI - Master Architecture Blueprint & Verification Walkthrough</title>
    <style>
        @page {{
            size: A4;
            margin: 12mm 12mm 12mm 12mm;
            @bottom-right {{
                content: counter(page);
            }}
        }}
        body {{
            background: #ffffff;
            color: #0f172a;
            font-family: Consolas, "Cascadia Code", "Courier New", monospace;
            font-size: 10px;
            line-height: 1.35;
            margin: 0;
            padding: 0;
        }}
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <pre>{escaped}</pre>
</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

cmd = [
    EDGE_EXE,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_DEST}",
    HTML_PATH
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0 and os.path.isfile(PDF_DEST):
    print(f"[OK] Successfully created: {PDF_DEST} ({os.path.getsize(PDF_DEST)} bytes)")
else:
    print(f"[!] Error: {res.stderr}")
