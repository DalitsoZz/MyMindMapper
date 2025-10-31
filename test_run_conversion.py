from mindmap_to_pdf import mindmap_to_pdf
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output = os.path.join(BASE_DIR, 'test_output.pdf')
plantuml = """@startmindmap
* Root
@endmindmap
"""
print('Running conversion test, output ->', output)
mindmap_to_pdf(plantuml, output_file=output)
print('Test finished.')
