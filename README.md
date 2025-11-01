MyMindMapper — concise, for visual learners

MyMindMapper Is a simple pyhthon/Java tool I worked that aids in visual learning by turning  plantuml text from lecture notes into there respectful mind map

Why this helps visual learners

- Turn linear notes into spatial structure so relationships are visible at a glance.
- Faster comprehension and recall: grouped, hierarchical layout highlights structure.
- Plain-text source: PlantUML text is easy to edit, diff, and script.

Quick workflow

1. Produce PlantUML mindmap text (use @startmindmap / @endmindmap):

   @startmindmap
   * Root Topic
   ** Topic A
   *** Subpoint A.1
   ** Topic B
   @endmindmap

2. Preview/edit in the GUI:

   python mindmap_gui.py

3. Convert to PDF (or SVG):

   python mindmap_to_pdf.py lecture.puml lecture.pdf

Optional NLP workflow

- You can use an NLP assistant or a script to extract headings and bullets from lecture notes or PDFs and produce PlantUML mindmap text programmatically.

Requirements

- Python 3.8+
- Java (JRE/JDK) on PATH for PlantUML/Batik usage
- Graphviz `dot` on PATH (recommended for PlantUML layouts)

Files of interest

- `mindmap_gui.py` — GUI editor/preview for PlantUML mindmaps
- `mindmap_to_pdf.py` — converter from PlantUML text (or generated SVG) to PDF
- `check_env.py` — quick environment checker (optional)

Quick checks

1) Verify environment:

   python check_env.py

2) Install Python deps in a venv (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Notes

- This repo may include `plantuml.jar` and a Batik distribution; the converter searches the app folder for required jars. If you prefer not to bundle those binaries in the repo, remove them and install externally.
- Be careful with private lecture material when using external NLP services.

If you want the README text changed or shortened further, tell me the exact wording and I'll update and push.
