import subprocess
import tempfile
import os
import sys
import glob
import shutil

# Resolve base directory (supports MYMINDMAP_BASE_DIR env override and PyInstaller)
def resolve_base_dir() -> str:
    env = os.environ.get("MYMINDMAP_BASE_DIR")
    if env:
        return env

    # PyInstaller: when frozen, sys._MEIPASS points to the temp folder with bundled data
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return meipass
        # fallback to the executable directory
        return os.path.dirname(sys.executable)

    # Running from source
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = resolve_base_dir()

def java_available():
    return shutil.which("java") is not None or JAVA_EXE is not None


def find_java_executable():
    # Prefer PATH java first
    p = shutil.which("java")
    if p:
        return p

    # Common Windows install locations
    candidates = [
        os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Java'),
        os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Zulu'),
        os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'AdoptOpenJDK'),
        os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'OpenJDK'),
        r'C:\Program Files',
        r'C:\Program Files (x86)',
    ]
    for base in candidates:
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            if 'java.exe' in files:
                return os.path.join(root, 'java.exe')

    return None


# locate java executable once
JAVA_EXE = find_java_executable()

def build_java_cmd(args):
    if JAVA_EXE:
        return [JAVA_EXE] + args
    return ["java"] + args

# Paths (try a few common locations)
def find_jar_recursive(base: str, names: list[str]) -> str | None:
    """Search base directory recursively for any jar whose basename matches one of names.
    names should be lower-case substrings to look for (e.g. 'batik-rasterizer-1.19.jar').
    Returns first matching path or None.
    """
    for root, _dirs, files in os.walk(base):
        for f in files:
            lf = f.lower()
            for name in names:
                if lf == name or name in lf:
                    return os.path.join(root, f)
    return None


# Find PlantUML jar in the app bundle or current working dir
PLANTUML_JAR = find_jar_recursive(BASE_DIR, ["plantuml.jar", "plantuml"])
if not PLANTUML_JAR:
    alt = find_jar_recursive(os.getcwd(), ["plantuml.jar", "plantuml"])
    if alt:
        PLANTUML_JAR = alt

# Find Batik jars or lib directory anywhere under BASE_DIR
BATIK_RASTERIZER_JAR = find_jar_recursive(BASE_DIR, ["batik-rasterizer-1.19.jar", "batik-rasterizer"])
BATIK_ALL_JAR = find_jar_recursive(BASE_DIR, ["batik-all-1.19.jar", "batik-all"]) if not BATIK_RASTERIZER_JAR else None

# Try to find a 'lib' directory that looks like a batik distribution
BATIK_LIB_DIR = None
for root, dirs, files in os.walk(BASE_DIR):
    if 'batik' in os.path.basename(root).lower() and 'lib' in dirs:
        cand = os.path.join(root, 'lib')
        # quick check for jar files inside
        if any(p.lower().endswith('.jar') for p in os.listdir(cand)):
            BATIK_LIB_DIR = cand
            break

# As an additional fallback, if a top-level 'batik-all-1.19.jar' exists in cwd, accept it
if not BATIK_RASTERIZER_JAR and not BATIK_ALL_JAR:
    cwd_batik = find_jar_recursive(os.getcwd(), ["batik-all-1.19.jar", "batik-all", "batik-rasterizer-1.19.jar"])
    if cwd_batik:
        if 'batik-all' in os.path.basename(cwd_batik).lower():
            BATIK_ALL_JAR = cwd_batik
        elif 'rasterizer' in os.path.basename(cwd_batik).lower():
            BATIK_RASTERIZER_JAR = cwd_batik

import datetime
# Optional fallback: cairosvg (pure-python) to convert SVG -> PDF if Batik fails
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except Exception:
    CAIROSVG_AVAILABLE = False

def mindmap_to_pdf(plantuml_code, output_file=None):
    # Generate unique output filename with timestamp if not provided
    if output_file is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(BASE_DIR, f"output_mindmap_{timestamp}.pdf")
    # Create isolated temporary directory for all intermediate files
    temp_dir = tempfile.mkdtemp(prefix="mindmap_")
    temp_puml = os.path.join(temp_dir, "diagram.puml")
    with open(temp_puml, "w", encoding="utf-8") as f:
        f.write(plantuml_code)

    try:
        # Validate java and jars before running
        if not java_available():
            print("❌ Error: 'java' not found on PATH. Install Java and try again.")
            return
        if not os.path.exists(PLANTUML_JAR):
            print(f"❌ Error: plantuml.jar not found at {PLANTUML_JAR}")
            return
        if not ((BATIK_RASTERIZER_JAR and os.path.exists(BATIK_RASTERIZER_JAR)) or (BATIK_LIB_DIR) or (BATIK_ALL_JAR and os.path.exists(BATIK_ALL_JAR))):
            print("❌ Error: Could not find a Batik rasterizer JAR or lib directory.")
            print("Base dir:", BASE_DIR)
            print("Searched for Batik/PlantUML jars under the base dir and current working dir. Details:")
            print("  PLANTUML_JAR:", PLANTUML_JAR)
            print("  BATIK_RASTERIZER_JAR:", BATIK_RASTERIZER_JAR)
            print("  BATIK_ALL_JAR:", BATIK_ALL_JAR)
            print("  BATIK_LIB_DIR:", BATIK_LIB_DIR)
            print("")
            print("Place the Batik distribution (batik-bin-1.19) or batik-rasterizer/batik-all jar inside the application folder, or set MYMINDMAP_BASE_DIR to your installation folder.")
            return
        # Step 1: Generate SVG with PlantUML (output will be created next to the .puml file)
        subprocess.run(
            build_java_cmd(["-jar", PLANTUML_JAR, "-tsvg", temp_puml]),
            check=True,
            cwd=temp_dir
        )

        # Find generated SVG file
        svg_file = os.path.join(temp_dir, "diagram.svg")
        if not os.path.exists(svg_file):
            # try fallback by name matching
            svgs = [p for p in os.listdir(temp_dir) if p.lower().endswith('.svg')]
            if svgs:
                svg_file = os.path.join(temp_dir, svgs[0])
            else:
                print("❌ Error: PlantUML did not produce an SVG file.")
                return

        # Step 2: Convert SVG to PDF using Batik rasterizer; try classpath-first to avoid launching SVGBrowser
        errors = []
        tried = []

        def try_cmd(cmd):
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True)
                tried.append((cmd, proc.returncode, proc.stdout, proc.stderr))
                return proc.returncode == 0
            except Exception as ex:
                tried.append((cmd, -1, "", str(ex)))
                return False

        # Candidate invocations in order of preference
        candidates = []
        if BATIK_LIB_DIR:
            cp = os.path.join(BATIK_LIB_DIR, "*")
            candidates.append(build_java_cmd(["-cp", cp, "org.apache.batik.apps.rasterizer.Main", "-m", "application/pdf", "-d", temp_dir, svg_file]))
            candidates.append(build_java_cmd(["-cp", cp, "org.apache.batik.apps.rasterizer.SVGConverter", "-m", "application/pdf", "-d", temp_dir, svg_file]))
        if BATIK_ALL_JAR:
            candidates.append(build_java_cmd(["-cp", BATIK_ALL_JAR, "org.apache.batik.apps.rasterizer.Main", "-m", "application/pdf", "-d", temp_dir, svg_file]))
            candidates.append(build_java_cmd(["-cp", BATIK_ALL_JAR, "org.apache.batik.apps.rasterizer.SVGConverter", "-m", "application/pdf", "-d", temp_dir, svg_file]))
        if BATIK_RASTERIZER_JAR and os.path.exists(BATIK_RASTERIZER_JAR):
            candidates.append(build_java_cmd(["-jar", BATIK_RASTERIZER_JAR, "-m", "application/pdf", "-d", temp_dir, svg_file]))

        success = False
        for cmd in candidates:
            success = try_cmd(cmd)
            if success:
                break

        if not success:
            print("❌ Batik conversion failed. Trying CairoSVG fallback (if available)...")
            for cmd, rc, out, err in tried:
                print("CMD:", " ".join(cmd))
                print("RET:", rc)
                if out:
                    print("STDOUT:")
                    print(out)
                if err:
                    print("STDERR:")
                    print(err)
                print("---")
            if CAIROSVG_AVAILABLE:
                try:
                    # Use cairosvg to convert SVG to PDF directly to produced_pdf
                    base = os.path.splitext(os.path.basename(svg_file))[0]
                    produced_pdf = os.path.join(temp_dir, base + ".pdf")
                    cairosvg.svg2pdf(url=svg_file, write_to=produced_pdf)
                    success = True
                except Exception as e:
                    print("❌ CairoSVG fallback failed:", e)
                    success = False
            else:
                print("❌ CairoSVG not available. Install with 'pip install cairosvg' to enable a Python fallback.")
                return

        # Locate produced PDF (same basename as SVG)
        base = os.path.splitext(os.path.basename(svg_file))[0]
        produced_pdf = os.path.join(temp_dir, base + ".pdf")
        if not os.path.exists(produced_pdf):
            # try any pdf in temp_dir
            pdfs = [p for p in os.listdir(temp_dir) if p.lower().endswith('.pdf')]
            if pdfs:
                produced_pdf = os.path.join(temp_dir, pdfs[0])
            else:
                print("❌ Error: Batik did not produce a PDF file in the temp directory.")
                return

        # Ensure destination directory exists
        dest_dir = os.path.dirname(output_file)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        # Move generated PDF to output location
        os.replace(produced_pdf, output_file)
        print(f"✅ PDF generated successfully: {output_file}")

    except subprocess.CalledProcessError as e:
        print("❌ Error running PlantUML or Batik:", e)
    finally:
        # Clean up the temporary directory and its contents
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


if __name__ == "__main__":
    print("📥 Paste your full PlantUML mindmap text below.")
    print("👉 Type END on a new line when you finish.\n")

    lines = []
    for line in sys.stdin:
        if line.strip() == "END":
            break
        lines.append(line)
    plantuml_code = "".join(lines)

    # Generate PDF with unique name
    mindmap_to_pdf(plantuml_code)
