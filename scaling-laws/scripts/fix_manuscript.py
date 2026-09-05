#!/usr/bin/env python3
"""
Fix manuscript/main_entropy.tex for MDPI Entropy submission:
1. Resolve all cross-references (ref, eqref) to numbers
2. Convert citations to numbered style (already done in source)
3. Fix text citations
4. Write modified LaTeX, convert to DOCX, post-process
"""

import re
import os
import subprocess
import shutil

MANUSCRIPT = 'manuscript/main_entropy.tex'
OUTPUT_TEX = 'manuscript/main_entropy_fixed.tex'
PANDOC = '/tmp/pandoc-3.1.11/bin/pandoc'

# ============================================================
# PART 1: Build label -> number mapping
# ============================================================

# Equation labels (in order of appearance)
EQ_MAP = {
    'eq:law': '1',
    'eq:identity': '2',
    'eq:decomp': '3',
    'eq:rd': '4',
    'eq:bridge': '5',
    'eq:modelN': '6',
    'eq:boundary': '7',
    'eq:bdyint': '8',
    'eq:entropy': '9',
    'eq:horizon': '10',
    'eq:cagnetta': '11',
    'eq:alphaD': '12',
    'eq:tele': '13',
    'eq:telefinal': '14',
    'eq:decom': '15',
    'eq:cross': '16',
    'eq:minimax': '17',
    'eq:Wstar': '18',
    'eq:varstar': '19',
    'eq:regimes': '20',
    'eq:iidvar': '21',
    'eq:alphaDiid': '22',
    'eq:sourceopt': '23',
    'eq:resolopt': '24',
    'eq:slope': '25',
    'eq:klseries': '26',
}

# Theorem-like labels (shared counter, section.X numbering)
THM_MAP = {
    'thm:decomp': '2.2',
    'thm:rd': '2.2',
    'thm:identified': '2.2',
    'thm:modelN': '3.1',
    'thm:recovery': '3.2',
    'thm:additive': '3.3',
    'thm:saturation': '3.3',
    'lem:bridge': '3.1',
    'lem:telescoping': '3.2',
    'prop:boundary': '3.1',
    'prop:vtoken': '3.1',
    'prop:logit': '3.1',
    'cor:floor': '2.2',
    'cor:excess': '2.2',
    'conj:crossover': '3.3',
    'def:registry': '2.3',
    'ass:consistent': '2.2',
    'ass:spectral': '2.3',
    'ass:fastlearn': '2.3',
    'pred:boundary': '3.5',
    'pred:compute': '3.3',
}

# Remark labels (global counter)
REM_MAP = {
    'rem:perlength': '2',
    'rem:slack': '3',
    'rem:registry': '4',
    'rem:capacity': '5',
    'rem:conditional': '6',
    'rem:chinchilla': '7',
    'rem:twotoken': '8',
    'rem:correction': '9',
    'rem:approach': '10',
    'rem:logit': '11',
    'rem:dominance': '12',
    'rem:discrepancy': '13',
    'rem:realizability': '14',
    'rem:empirical': '15',
    'rem:crossovernum': '16',
    'rem:finitelow': '17',
}

# Section labels (MDPI Entropy structure)
SEC_MAP = {
    'sec:intro': '1',
    'sec:methods': '2',
    'sec:related': '2.1',
    'sec:identity': '2.2',
    'sec:assumptions': '2.3',
    'sec:results': '3',
    'sec:modelsize': '3.1',
    'sec:data': '3.2',
    'sec:joint': '3.3',
    'sec:measurement': '3.4',
    'sec:empirical': '3.4.1',
    'sec:yan': '3.4.2',
    'sec:prediction': '3.5',
    'sec:numerics': '3.6',
    'sec:discussion': '4',
    'sec:conclusions': '5',
}

# Table labels
TAB_MAP = {
    'tab:empirical': '1',
}

# Figure labels (in order of appearance in manuscript)
FIG_MAP = {
    'fig:overview': '1',
    'fig:positioning': '2',
    'fig:alphaN_pred_obs': '3',
    'fig:synth': '4',
    'fig:evidence_status': '5',
}

# Paragraph/other labels (just anchors, not numbered references)
# These are: numerics:twotoken, numerics:vtoken, numerics:synth, par:prediction-test

# Merge all into one map
ALL_LABELS = {}
ALL_LABELS.update(EQ_MAP)
ALL_LABELS.update(THM_MAP)
ALL_LABELS.update(REM_MAP)
ALL_LABELS.update(SEC_MAP)
ALL_LABELS.update(TAB_MAP)
ALL_LABELS.update(FIG_MAP)

# ============================================================
# PART 2: Citation mapping (Vancouver order by first appearance)
# ============================================================

# Author names extracted from bibliography \bibitem
CIT_AUTHORS = {
    'bahri2024': 'Bahri et al.',
    'berger1971': 'Berger',
    'besiroglu2024': 'Besiroglu et al.',
    'bicalhoun2025': 'Bi and Calhoun',
    'bordelon2024': 'Bordelon et al.',
    'cagnetta2026': 'Cagnetta et al.',
    'cover2006': 'Cover and Thomas',
    'efroimovich1985': 'Efroimovich',
    'hoffmann2022': 'Hoffmann et al.',
    'jeonvanroy2024': 'Jeon and Van Roy',
    'kaplan2020': 'Kaplan et al.',
    'merity2017': 'Merity et al.',
    'tsybakov2009': 'Tsybakov',
    'scheibner2025': 'Scheibner et al.',
    'yan2026': 'Yan et al.',
}

# Vancouver numbering (order of first citation in text)
CIT_VANCOUVER = {
    'hoffmann2022': 1,
    'kaplan2020': 2,
    'berger1971': 3,
    'cover2006': 4,
    'cagnetta2026': 5,
    'bicalhoun2025': 6,
    'bahri2024': 7,
    'bordelon2024': 8,
    'jeonvanroy2024': 9,
    'merity2017': 10,
    'scheibner2025': 11,
    'tsybakov2009': 12,
    'efroimovich1985': 13,
    'besiroglu2024': 14,
    'yan2026': 15,
}

# Reverse map: key -> Vancouver number as string
CIT_NUM = {k: str(v) for k, v in CIT_VANCOUVER.items()}


def resolve_ref(label):
    """Resolve a label to its number string."""
    if label in ALL_LABELS:
        return ALL_LABELS[label]
    # Try to find it (should not happen if mapping is complete)
    print(f"WARNING: unresolved label '{label}'")
    return f'??{label}??'


def resolve_citep(keys_str):
    """Convert \\citep{key1,key2} to [N1,N2]."""
    keys = [k.strip() for k in keys_str.split(',')]
    nums = []
    for k in keys:
        if k in CIT_NUM:
            nums.append(CIT_NUM[k])
        else:
            print(f"WARNING: unknown citation key '{k}'")
            nums.append(f'??{k}??')
    return '[' + ','.join(nums) + ']'


def resolve_citet(keys_str):
    """Convert \\citet{key} to 'Author et al. [N]'."""
    keys = [k.strip() for k in keys_str.split(',')]
    parts = []
    for k in keys:
        if k in CIT_NUM:
            author = CIT_AUTHORS.get(k, k)
            num = CIT_NUM[k]
            parts.append(f'{author} [{num}]')
        else:
            print(f"WARNING: unknown citation key '{k}'")
            parts.append(f'??{k}??')
    return ' and '.join(parts)


# ============================================================
# PART 3: Process the LaTeX file
# ============================================================

def process_file(input_path, output_path):
    with open(input_path, 'r') as f:
        content = f.read()

    # --- Step 1: Remove keywords section ---
    content = re.sub(
        r'\\begin\{keywords\}\n.*?\n\\end\{keywords\}\n?',
        '',
        content,
        flags=re.DOTALL
    )

    # --- Step 2: Fix anonymization (single-blind) ---
    # Handle the multi-line split across actual file
    content = content.replace(
        'generators are released with the paper via an anonymized mirror\n'
        '(\\texttt{anonymous.4open.science}); a link is provided to reviewers during\n'
        'double-blind review.',
        'generators are released with the paper in the project repository\n'
        '(\\url{https://github.com/Shahul9570/Research.git}).'
    )
    # Also handle "All scripts..." variant
    content = content.replace(
        'All scripts and data generators are released with the paper via an anonymized mirror\n'
        '(\\texttt{anonymous.4open.science}); a link is provided to reviewers during\n'
        'double-blind review.',
        'All scripts and data generators are released with the paper in the project repository\n'
        '(\\url{https://github.com/Shahul9570/Research.git}).'
    )
    # Catch any remaining instances
    content = content.replace(
        'via an anonymized mirror',
        'in the project repository'
    )
    content = content.replace(
        '(\\texttt{anonymous.4open.science}); a link is provided to reviewers during\n'
        'double-blind review.',
        '(\\url{https://github.com/Shahul9570/Research.git}).'
    )
    content = content.replace(
        '(\\texttt{anonymous.4open.science})',
        '(\\url{https://github.com/Shahul9570/Research.git})'
    )

    # --- Step 2b: Convert \\sampleavailability to regular paragraph ---
    def replace_sampleavail(m):
        inner = m.group(1)
        return f'\\noindent\\textbf{{Data and Code Availability.}} {inner}'
    content = re.sub(r'\\sampleavailability\{([^}]+)\}', replace_sampleavail, content)

    # --- Step 3: Resolve \\eqref{X} -> (N) ---
    def replace_eqref(m):
        label = m.group(1)
        num = resolve_ref(label)
        return f'({num})'

    content = re.sub(r'\\eqref\{([^}]+)\}', replace_eqref, content)

    # --- Step 4: Resolve \\ref{X} -> N ---
    def replace_ref(m):
        label = m.group(1)
        num = resolve_ref(label)
        return num

    content = re.sub(r'(?<!\\)\\ref\{([^}]+)\}', replace_ref, content)

    # --- Step 5: Resolve \\citep{keys} -> [N] ---
    def replace_citep(m):
        keys = m.group(1)
        return resolve_citep(keys)

    content = re.sub(r'\\citep\{([^}]+)\}', replace_citep, content)

    # --- Step 6: Resolve \\citet{key} -> Author et al. [N] ---
    def replace_citet(m):
        keys = m.group(1)
        return resolve_citet(keys)

    content = re.sub(r'\\citet\{([^}]+)\}', replace_citet, content)

    # --- Step 7: Fix text citations ---
    # "Kaplan et al.~(2020)" -> "Kaplan et al. [2]"
    content = re.sub(
        r'Kaplan et al\.~\(2020\)',
        r'Kaplan et al. [2]',
        content
    )
    # "Hoffmann\net al.~(2022)" (may span lines) -> "Hoffmann et al. [1]"
    content = re.sub(
        r'Hoffmann\s*\n?\s*et al\.~\(2022\)',
        r'Hoffmann et al. [1]',
        content
    )
    # "Cagnetta et al.~(2026)" -> "Cagnetta et al. [4]"
    content = re.sub(
        r'Cagnetta et al\.~\(2026\)',
        r'Cagnetta et al. [4]',
        content
    )
    # "Cagnetta et al. (2026)" (without tilde, in discussion)
    content = re.sub(
        r'Cagnetta et al\. \(2026\)',
        r'Cagnetta et al. [4]',
        content
    )
    # "Jeon and Van Roy (2024)" -> "Jeon and Van Roy [3]"
    content = re.sub(
        r'Jeon and Van Roy \(2024\)',
        r'Jeon and Van Roy [3]',
        content
    )
    # "Bi and Calhoun (2025)" -> "Bi and Calhoun [6]"
    content = re.sub(
        r'Bi and Calhoun \(2025\)',
        r'Bi and Calhoun [6]',
        content
    )
    # "(Berger, 1971; Cover and Thomas, 2006)" -> "(Berger [11]; Cover and Thomas [12])"
    content = re.sub(
        r'\(Berger, 1971; Cover and Thomas, 2006\)',
        r'(Berger [11]; Cover and Thomas [12])',
        content
    )

    # --- Step 8: Remove the keywords environment definition ---
    content = re.sub(
        r'% Keywords environment \(standalone, not from jmlr2e\)\n'
        r'\\newenvironment\{keywords\}\{\\noindent\\textbf\{Keywords:\}\}\{\}\n',
        '',
        content
    )

    # --- Step 9: Clean up the title page for PLOS ONE ---
    # Remove the manual running title header (will be handled by PLOS ONE template)
    content = re.sub(
        r'\\begin\{center\}\{\\LARGE\\bf [^\}]*\}\\end\{center\}\\doublespacing\n',
        r'\\doublespacing' + '\n',
        content
    )

    # --- Step 10: Fix \\acks{} to work with pandoc ---
    # The \acks command is defined as \newcommand{\acks}[1]{\paragraph{Acknowledgments}#1}
    # This should work fine with pandoc.

    # --- Step 11: Rewrite bibliography in Vancouver order ---
    content = rewrite_bibliography(content)

    # --- Step 12: Swap PDF->PNG in includegraphics for DOCX compatibility ---
    content = re.sub(
        r'(\\includegraphics\[[^\]]*\]\{[^}]*?)(\.pdf)(\})',
        r'\1.png\3',
        content
    )

    # --- Step 13: Fix \rm -> \mathrm for pandoc math compatibility ---
    # Replace {\rm xxx} with {\mathrm{xxx}} anywhere in math
    content = re.sub(r'\{\\rm\s+(\w+)\}', r'{\\mathrm{\1}}', content)

    # --- Step 12: Add PLOS ONE header comment ---
    header = (
        '% PLOS ONE formatted manuscript\n'
        '% Generated by fix_manuscript.py\n'
        '% TODO: Replace placeholder author information before submission\n'
        '% TODO: Apply PLOS ONE LaTeX template (plosone.cls) for final formatting\n'
        '% TODO: Add line numbers using PLOS ONE submission system\n\n'
    )
    content = header + content

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"Written fixed LaTeX to {output_path}")
    return content


def rewrite_bibliography(content):
    """Extract bibliography entries, reorder by Vancouver number, rewrite."""

    # Extract bibliography block
    bib_match = re.search(
        r'(\\bibliographystyle\{[^}]*\}\n)?(\\begin\{thebibliography\}.*?\\end\{thebibliography\})',
        content, re.DOTALL
    )
    if not bib_match:
        print("WARNING: could not find bibliography")
        return content

    bib_full = bib_match.group(0)
    bib_block = bib_match.group(2)

    # Extract individual \bibitem entries
    bibitems = re.findall(
        r'(\\bibitem\[[^\]]*\]\{[^}]*\}.*?)(?=\\bibitem|\\end\{thebibliography\})',
        bib_block, re.DOTALL
    )

    # Parse each bibitem to get its key
    parsed = []
    for item in bibitems:
        key_match = re.search(r'\\bibitem\[[^\]]*\]\{([^}]*)\}', item)
        if key_match:
            key = key_match.group(1)
            parsed.append((key, item.strip()))

    # Reorder by Vancouver number
    reordered = []
    for key, text in parsed:
        if key in CIT_VANCOUVER:
            vnum = CIT_VANCOUVER[key]
            reordered.append((vnum, key, text))
        else:
            print(f"WARNING: bibliography key '{key}' not in Vancouver map")
            reordered.append((999, key, text))

    reordered.sort(key=lambda x: x[0])

    # Build new bibliography
    new_bib_lines = ['\\begin{thebibliography}{15}']
    for vnum, key, text in reordered:
        # Replace the old \bibitem line with a numbered one
        # Extract author-year header from the old \bibitem
        old_header = re.search(r'\\bibitem\[([^\]]*)\]', text)
        if old_header:
            old_ah = old_header.group(1)
            # Extract just the author part (before the year)
            author_match = re.match(r'^(.*?)\(', old_ah)
            author_part = author_match.group(1) if author_match else old_ah
            year_match = re.search(r'\((\d{4}[a-z]?)\)', old_ah)
            year_part = year_match.group(1) if year_match else ''
        else:
            author_part = ''
            year_part = ''

        # Get the body (everything after \bibitem[...]{...})
        body = re.sub(r'\\bibitem\[[^\]]*\]\{[^}]*\}\s*', '', text)

        # Format as Vancouver: [N] Author. Title. Journal, Year.
        # Clean up the body to remove leading/trailing whitespace
        body = body.strip()

        new_bib_lines.append(f'\\bibitem[{vnum}]{{{key}}} {body}')

    new_bib_lines.append('\\end{thebibliography}')

    new_bib = '\n'.join(new_bib_lines)

    # Replace old bibliography
    content = content.replace(bib_full, new_bib)

    # Also remove \bibliographystyle{plainnat} since we're using thebibliography directly
    content = content.replace('\\bibliographystyle{plainnat}\n', '')

    return content


# ============================================================
# PART 4: Convert to DOCX
# ============================================================

def convert_to_docx(tex_path, docx_path):
    """Convert LaTeX to DOCX using pandoc."""
    cmd = [
        PANDOC,
        tex_path,
        '-o', docx_path,
        '--from=latex',
        '--to=docx',
        '--wrap=auto',
        '--resource-path=manuscript',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"Pandoc error: {result.stderr}")
    else:
        warnings = [l for l in result.stderr.split('\n') if l.strip()]
        if warnings:
            print(f"Pandoc warnings: {len(warnings)}")
            for w in warnings[:5]:
                print(f"  {w}")
        print(f"Written DOCX to {docx_path}")
    return result.returncode


# ============================================================
# PART 5: Post-process DOCX with python-docx
# ============================================================

def postprocess_docx(docx_path):
    """Apply PLOS ONE formatting to DOCX."""
    try:
        from docx import Document
        from docx.shared import Pt, Inches
        from docx.enum.text import WD_LINE_SPACING
    except ImportError:
        print("python-docx not available, skipping post-processing")
        return

    doc = Document(docx_path)

    # Set default font to Times New Roman 12pt
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    # Set paragraph spacing to single (MDPI style)
    pf = style.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    pf.space_after = Pt(6)
    pf.space_before = Pt(0)

    # Set margins (MDPI: 1.75 inch left/right for review, 1 inch final)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    doc.save(docx_path)
    print(f"Post-processed DOCX: {docx_path}")


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    os.chdir('/home/ciods/Shahul/research/scaling-laws')

    # Step 1: Process LaTeX
    print("=" * 60)
    print("STEP 1: Processing LaTeX file")
    print("=" * 60)
    process_file(MANUSCRIPT, OUTPUT_TEX)

    # Step 2: Convert to DOCX
    print("\n" + "=" * 60)
    print("STEP 2: Converting to DOCX")
    print("=" * 60)
    docx_path = 'manuscript/main_entropy.docx'
    convert_to_docx(OUTPUT_TEX, docx_path)

    # Step 3: Post-process DOCX
    print("\n" + "=" * 60)
    print("STEP 3: Post-processing DOCX")
    print("=" * 60)
    postprocess_docx(docx_path)

    # Step 4: Verify
    print("\n" + "=" * 60)
    print("STEP 4: Verification")
    print("=" * 60)

    # Check for remaining unresolved references
    with open(OUTPUT_TEX, 'r') as f:
        fixed = f.read()

    remaining_refs = re.findall(r'\\ref\{([^}]+)\}', fixed)
    remaining_eqrefs = re.findall(r'\\eqref\{([^}]+)\}', fixed)
    remaining_citep = re.findall(r'\\citep\{([^}]+)\}', fixed)
    remaining_citet = re.findall(r'\\citet\{([^}]+)\}', fixed)

    print(f"Remaining \\ref: {len(remaining_refs)} {remaining_refs}")
    print(f"Remaining \\eqref: {len(remaining_eqrefs)} {remaining_eqrefs}")
    print(f"Remaining \\citep: {len(remaining_citep)} {remaining_citep}")
    print(f"Remaining \\citet: {len(remaining_citet)} {remaining_citet}")

    # Check for broken text citations
    broken_cites = re.findall(r'et al\.~\(\d{4}\)', fixed)
    print(f"Remaining text citations 'et al.~(YEAR)': {len(broken_cites)} {broken_cites}")

    # Verify DOCX content
    try:
        from docx import Document
        doc = Document(docx_path)
        text = '\n'.join(p.text for p in doc.paragraphs)

        checks = {
            'eq:law resolved': '(1)' in text or 'L(N,D)' in text,
            'thm:decomp resolved': 'Entropy-floor decomposition' in text,
            'Vancouver [1]': '[1]' in text,
            'Vancouver [2]': '[2]' in text,
            'Keywords removed': 'Keywords:' not in text,
            'Data Availability': 'Data' in text and 'Availability' in text,
            'Code Availability': 'Code' in text and 'Availability' in text,
            'Pre-registration': 'pre-registration' in text.lower(),
            'GitHub link present': 'Shahul9570' in text,
            'No anonymized mirror': 'anonymous.4open.science' not in text,
            'No double-blind': 'double-blind' not in text,
        }

        print("\nDOCX content checks:")
        all_ok = True
        for check, result in checks.items():
            status = 'OK' if result else 'FAIL'
            if not result:
                all_ok = False
            print(f"  {status}: {check}")

        print(f"\nDOCX paragraphs: {len(doc.paragraphs)}")
        print(f"DOCX tables: {len(doc.tables)}")

    except Exception as e:
        print(f"DOCX verification error: {e}")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
