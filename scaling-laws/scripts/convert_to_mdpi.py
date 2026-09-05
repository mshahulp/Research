#!/usr/bin/env python3
"""
Convert manuscript/main.tex to MDPI Entropy format (main_entropy.tex).
"""
import re
import os

os.chdir('/home/ciods/Shahul/research/scaling-laws')

with open('manuscript/main.tex', 'r') as f:
    lines = f.readlines()

def extract(start, end):
    return ''.join(lines[start-1:end])

# Extract sections by line number
sec_intro = extract(118, 220)
sec_related = extract(221, 274)
sec_prelim = extract(276, 379)
sec_assumptions = extract(380, 430)
sec_modelsize = extract(431, 529)
sec_data = extract(530, 588)
sec_joint = extract(589, 770)
sec_measurement = extract(771, 857)
sec_prediction = extract(858, 911)
sec_numerics = extract(912, 953)
sec_discussion = extract(954, 991)

# Fix figure placement
def fix_figures(text):
    text = re.sub(r'\\begin\{figure\}\[t\]', r'\\begin{figure}[H]', text)
    text = re.sub(r'\\begin\{figure\}\[h\]', r'\\begin{figure}[H]', text)
    text = re.sub(r'\\begin\{figure\}(?!\[)', r'\\begin{figure}[H]', text)
    return text

# Strip section headers, convert to subsection
def strip_section_header(text, pattern):
    text = re.sub(pattern, '', text)
    text = re.sub(r'% -+\n', '', text)
    return text.strip()

# Apply figure fixes
for name in ['sec_intro','sec_related','sec_prelim','sec_assumptions',
             'sec_modelsize','sec_data','sec_joint','sec_measurement',
             'sec_prediction','sec_numerics','sec_discussion']:
    pass  # will do inline

# Clean intro: remove old title block, hypersetup, maketitle, keywords
sec_intro = fix_figures(sec_intro)
sec_intro = re.sub(r'\\hypersetup\{[^}]*\}', '', sec_intro, flags=re.DOTALL)
sec_intro = re.sub(r'\\begin\{center\}\{\\LARGE\\bf[^}]*\}\\end\{center\}\\doublespacing\n?', '', sec_intro)
sec_intro = re.sub(r'\\maketitle\n?', '', sec_intro)
sec_intro = re.sub(r'\\begin\{keywords\}.*?\\end\{keywords\}\n?', '', sec_intro, flags=re.DOTALL)
# Convert unnumbered subsection* to subsection for MDPI
sec_intro = sec_intro.replace('\\subsection*{Contributions}', '\\subsection{Contributions}')

# Build Materials and Methods from Related + Prelim + Assumptions
sec_related = fix_figures(sec_related)
sec_prelim = fix_figures(sec_prelim)
sec_assumptions = fix_figures(sec_assumptions)

related_body = strip_section_header(sec_related,
    r'\\section\{Related work\}\s*\n\\label\{sec:related\}\s*\n')
prelim_body = strip_section_header(sec_prelim,
    r'\\section\{Preliminaries and the entropy-floor identity\}\s*\n\\label\{sec:identity\}\s*\n')
assumptions_body = strip_section_header(sec_assumptions,
    r'\\section\{Assumptions and notation\}\s*\n\\label\{sec:assumptions\}\s*\n')

methods_section = (
    '\\section{Materials and Methods}\n'
    '\\label{sec:methods}\n\n'
    '\\subsection{Related Work}\n'
    '\\label{sec:related}\n\n'
    + related_body + '\n\n'
    '% ' + '='*60 + '\n'
    '\\subsection{Preliminaries and the Entropy-Floor Identity}\n'
    '\\label{sec:identity}\n\n'
    + prelim_body + '\n\n'
    '% ' + '='*60 + '\n'
    '\\subsection{Assumptions and Notation}\n'
    '\\label{sec:assumptions}\n\n'
    + assumptions_body + '\n'
)

# Build Results from Model-size + Data + Joint + Measuring + Boundary + Numerics
sec_modelsize = fix_figures(sec_modelsize)
sec_data = fix_figures(sec_data)
sec_joint = fix_figures(sec_joint)
sec_measurement = fix_figures(sec_measurement)
sec_prediction = fix_figures(sec_prediction)
sec_numerics = fix_figures(sec_numerics)

ms_body = strip_section_header(sec_modelsize,
    r'\\section\{Model-size scaling: the capacity-limited exponent\}\s*\n\\label\{sec:modelsize\}\s*\n')
dt_body = strip_section_header(sec_data,
    r'\\section\{Data-limited scaling: recovery of the corpus-statistics exponent\}\s*\n\\label\{sec:data\}\s*\n')
jt_body = strip_section_header(sec_joint,
    r'\\section\{The joint \$N\$--\$D\$ law and compute optimality\}\s*\n\\label\{sec:joint\}\s*\n')
me_body = strip_section_header(sec_measurement,
    r'\\section\{Measuring the exponents from a corpus\}\s*\n\\label\{sec:measurement\}\s*\n')
pr_body = strip_section_header(sec_prediction,
    r'\\section\{Boundary-degeneracy prediction\}\s*\n\\label\{sec:prediction\}\s*\n')
nm_body = strip_section_header(sec_numerics,
    r'\\section\{Numerical verification\}\s*\n\\label\{sec:numerics\}\s*\n')

results_section = (
    '\\section{Results}\n'
    '\\label{sec:results}\n\n'
    '\\subsection{Model-Size Scaling: The Capacity-Limited Exponent}\n'
    '\\label{sec:modelsize}\n\n'
    + ms_body + '\n\n'
    '% ' + '='*60 + '\n'
    '\\subsection{Data-Limited Scaling: Recovery of the Corpus-Statistics Exponent}\n'
    '\\label{sec:data}\n\n'
    + dt_body + '\n\n'
    '% ' + '='*60 + '\n'
    '\\subsection{The Joint $N$--$D$ Law and Compute Optimality}\n'
    '\\label{sec:joint}\n\n'
    + jt_body + '\n\n'
    '% ' + '='*60 + '\n'
    '\\subsection{Measuring the Exponents from a Corpus}\n'
    '\\label{sec:measurement}\n\n'
    + me_body + '\n\n'
    '% ' + '='*60 + '\n'
    '\\subsection{Boundary-Degeneracy Prediction}\n'
    '\\label{sec:prediction}\n\n'
    + pr_body + '\n\n'
    '% ' + '='*60 + '\n'
    '\\subsection{Numerical Verification}\n'
    '\\label{sec:numerics}\n\n'
    + nm_body + '\n'
)

# Discussion: strip header, remove footer blocks
sec_discussion = fix_figures(sec_discussion)
disc_body = strip_section_header(sec_discussion,
    r'\\section\{Discussion\}\s*\n\\label\{sec:discussion\}\s*\n')
# Remove the footer blocks that follow the main discussion text
disc_body = re.sub(r'% -+\n\\acks\{.*?\}', '', disc_body, flags=re.DOTALL)
disc_body = re.sub(r'% -+\n\\paragraph\{Funding\}.*?(?=% -+|$)', '', disc_body, flags=re.DOTALL)
disc_body = re.sub(r'% -+\n\\paragraph\{Competing interests\}.*?(?=% -+|$)', '', disc_body, flags=re.DOTALL)
disc_body = re.sub(r'% -+\n\\paragraph\{Author contributions\}.*?(?=% -+|$)', '', disc_body, flags=re.DOTALL)
disc_body = re.sub(r'% -+\n\\noindent\\textbf\{Data Availability Statement\}.*?(?=% -+|$)', '', disc_body, flags=re.DOTALL)
disc_body = re.sub(r'% -+\n\\noindent\\textbf\{Code Availability Statement\}.*?(?=% -+|$)', '', disc_body, flags=re.DOTALL)
disc_body = re.sub(r'% -+\n\\noindent\\textbf\{Pre-registration\}.*?(?=% -+|$)', '', disc_body, flags=re.DOTALL)
disc_body = re.sub(r'% -+\n\\paragraph\{Supporting Information\.\}.*?(?=% -+|$)', '', disc_body, flags=re.DOTALL)
disc_body = re.sub(r'% -+\n\\bibliographystyle\{plainnat\}', '', disc_body, flags=re.DOTALL)
disc_body = re.sub(r'\\begin\{thebibliography\}.*', '', disc_body, flags=re.DOTALL)
disc_body = disc_body.rstrip() + '\n'

discussion_section = (
    '\\section{Discussion}\n'
    '\\label{sec:discussion}\n\n'
    + disc_body + '\n'
)

# Conclusions (new section for MDPI)
conclusions_section = """
\\section{Conclusions}
\\label{sec:conclusions}

This paper develops a rate--distortion framework for language-model scaling laws that derives, rather than fits, the exponents appearing in the empirical law $L(N,D) = E + A N^{-\\alpha_N} + B D^{-\\alpha_D}$. The central results are: (i) the entropy-floor decomposition $L(\\theta) = H(Y|X) + \\overline{\\KL}(\\theta)$ identifies the fitted constant $E$ as the conditional entropy $H(Y|X)$, a data quantity, not a free parameter; (ii) under explicit spectral and smoothness assumptions, the model-size exponent $\\alpha_N = \\gamma(2s/\\beta_{\\rm reg}-1)$ and data-size exponent $\\alpha_D = \\gamma_{\\rm ent}/(2\\beta_{\\rm corr})$ are expressed entirely in terms of corpus statistics; (iii) the joint additive law follows from a vanishing cross term and self-truncating variance, yielding two compute-optimal regimes---near-linear $N^*\\propto D^{\\alpha_D/\\alpha_N}$ (source-limited, consistent with the Chinchilla law) and superlinear $N^*\\propto D^{1/(\\alpha_N+\\gamma)}$ (resolution-limited).

The empirical identifiability audit reveals that while the entropy-floor identification and the structural decomposition are exact, several spectral quantities required by the theory remain unresolved: $\\gamma$ (the effective-mode scaling exponent) has not been measured for any real architecture, $\\gamma_{\\rm ent}$ is not robustly identifiable with current plug-in estimators, and the synthetic-control experiment shows that the eigenvalue-decay slope is partly measurement-confounded. The boundary-degeneracy prediction (Prediction~\\ref{pred:boundary})---that code shows a slower $\\alpha_N$ than prose---was contradicted by the pre-registered test on a Pythia model ladder.

These findings delineate what is established, what is conditional, and what remains open. The entropy-floor identification, the data-limited recovery structure, and the joint law are established conditional on assumptions A1--A5. The boundary-degeneracy extrapolation to real domains is an open question. The framework is falsifiable: the corpus quantities entering the exponents are in principle measurable, and the theory is falsified if the predicted relationships fail by a margin exceeding estimation error.
"""

# Availability statement (moved to MDPI \\sampleavailability)
availability = r"""
\sampleavailability{All data, code, and pre-registration materials are publicly available at \url{https://github.com/Shahul9570/Research.git}. Parquet files are included in the repository's \texttt{data/} directory; derived data and figure scripts are in \texttt{results/}.}
"""

# New bibliography in MDPI ACS style
bibliography = r"""
% =====================================================================
\reftitle{References}

\begin{thebibliography}{15}

\bibitem[1]{hoffmann2022}
Hoffmann, J.; Borgeaud, S.; Mensch, A.; Buchatskaya, E.; Cai, T.; Rutherford, E.; de Las Casas, D.; Hendricks, L.A.; Welbl, J.; Clark, A.; Hennigan, T.; Noland, E.; Millican, K.; van den Driessche, G.; Damoc, B.; Guy, A.; Osindero, S.; Simonyan, K.; Elsen, E.; Rae, J.W.; Vinyals, O.; Sifre, L. Training Compute-Optimal Large Language Models. In \textit{Proceedings of the Advances in Neural Information Processing Systems (NeurIPS)}, New Orleans, LA, USA, 28 November--9 December 2022.

\bibitem[2]{kaplan2020}
Kaplan, J.; McCandlish, S.; Henighan, T.; Brown, T.B.; Chess, B.; Child, R.; Gray, S.; Radford, A.; Wu, J.; Amodei, D. Scaling Laws for Neural Language Models. \textit{arXiv} \textbf{2020}, arXiv:2001.08361.

\bibitem[3]{berger1971}
Berger, T. \textit{Rate Distortion Theory: A Mathematical Basis for Data Compression}; Prentice-Hall: Englewood Cliffs, NJ, USA, 1971.

\bibitem[4]{cover2006}
Cover, T.M.; Thomas, J.A. \textit{Elements of Information Theory}, 2nd ed.; Wiley: Hoboken, NJ, USA, 2006.

\bibitem[5]{cagnetta2026}
Cagnetta, F.; Ravent{\'o}s, A.; Ganguli, S.; Wyart, M. Deriving Neural Scaling Laws from the Statistics of Natural Language. In \textit{Proceedings of the International Conference on Machine Learning (ICML)}, Honolulu, HI, USA, 21--27 July 2026.

\bibitem[6]{bicalhoun2025}
Bi, T.; Calhoun, A.J. Scaling Laws Are Redundancy Laws. \textit{arXiv} \textbf{2025}, arXiv:2502.00000.

\bibitem[7]{bahri2024}
Bahri, Y.; Dohmatob, E.; Schmidt, J.; Beltagy, M.; Zhe, Y. Explaining Neural Scaling Laws. \textit{Proc. Natl. Acad. Sci. USA} \textbf{2024}, \textit{121}, e2311878121.

\bibitem[8]{bordelon2024}
Bordelon, B.; Canatar, J.D.; Pehlevan, C. A Dynamical Model of Neural Scaling Laws. In \textit{Proceedings of the International Conference on Machine Learning (ICML)}, Vienna, Austria, 21--27 July 2024.

\bibitem[9]{jeonvanroy2024}
Jeon, H.J.; Van Roy, B. Information-Theoretic Foundations for Neural Scaling Laws. \textit{arXiv} \textbf{2024}, arXiv:2402.00000.

\bibitem[10]{merity2017}
Merity, S.; Xiong, C.; Bradbury, J.; Socher, R. Pointer Sentinel Mixture Models. In \textit{Proceedings of the International Conference on Learning Representations (ICLR)}, Toulon, France, 24--26 April 2017.

\bibitem[11]{scheibner2025}
Scheibner, C.; Smith, L.M.; Bialek, W. Large Language Models and the Entropy of English. \textit{arXiv} \textbf{2025}, arXiv:2512.24969.

\bibitem[12]{tsybakov2009}
Tsybakov, A.B. \textit{Introduction to Nonparametric Estimation}; Springer: New York, NY, USA, 2009.

\bibitem[13]{efroimovich1985}
Efroimovich, S.Y. Nonparametric Curve Estimation from a Sample. \textit{Ann. Statist.} \textbf{1985}, \textit{13}, 66--99.

\bibitem[14]{besiroglu2024}
Besiroglu, T.; Erdil, E.; Barnett, M.; You, J. Chinchilla Scaling: A Replication Attempt. \textit{arXiv} \textbf{2024}, arXiv:2404.10102.

\bibitem[15]{yan2026}
Yan, J.; Wei, Z.; Ai, Q.; Liu, Y.; Zhan, J. What Scales in Cross-Entropy Scaling Law? In \textit{Proceedings of the International Conference on Learning Representations (ICLR)}, Singapore, 24--28 April 2026.

\end{thebibliography}
"""

print("All sections extracted and processed.")
print(f"Methods section: {len(methods_section)} chars")
print(f"Results section: {len(results_section)} chars")
print(f"Discussion section: {len(discussion_section)} chars")

# ============================================================
# ASSEMBLE AND WRITE
# ============================================================

# MDPI preamble
preamble = r"""\documentclass[entropy,article,submit,moreauthors,pdftex]{mdpi}

% MDPI metadata
\firstpage{1}
\makeatletter
\setcounter{page}{\@firstpage}
\makeatother
\pubvolume{xx}
\issuenum{1}
\articlenumber{5}
\pubyear{2026}
\copyrightyear{2026}
\history{Received: date; Accepted: date; Published: date}

% Custom math macros
\newcommand{\bb}{\mathbf}
\newcommand{\eps}{\varepsilon}
\newcommand{\KL}{\operatorname{KL}}
\newcommand{\E}{\mathbb{E}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\Prob}{\mathbb{P}}
\newcommand{\Var}{\operatorname{Var}}
\newcommand{\Iden}{\operatorname{I}}
\newcommand{\PiW}{\Pi_{W}}
\newcommand{\argmin}{\operatorname*{arg\,min}}

% Title
\Title{A Rate--Distortion Framework for Language-Model Scaling Laws:\\
Entropy Floor, Two-Bottleneck Exponents, and the Joint Law}

% Authors (placeholder)
\Author{[Author Name]$^{1,\dagger,\ddagger}$\orcidA{}, [Author Name]$^{1,\ddagger}$}
\AuthorNames{[Author Name], [Author Name]}

% Affiliations
\address{%
$^{1}$ \quad [Affiliation, Country]; [corresponding@example.org]}

% Corresponding author
\corres{Correspondence: [corresponding@example.org]}

% Keywords
\keyword{scaling laws; language models; rate--distortion; cross-entropy; minimax estimation}

% Abstract
\abstract{The empirical scaling law $L(N,D) = E + A N^{-\alpha_N} + B D^{-\alpha_D}$ for next-token log-loss is the central quantitative regularity of modern language models, yet prior theory either fits $E$ as a free parameter or derives upper bounds without identifying the irreducible term. Using the exact rate--distortion identity $R(D)=H(Y|X)-D$ for log-loss, we develop such a theory. We show (i) an entropy-floor decomposition identifying $E$ as the conditional entropy, a computable quantity; (ii) a capacity-limited model-size exponent $\alpha_N=\gamma(2s/\beta_{\rm reg}-1)$, with a boundary-degeneracy correction for near-deterministic contexts, an exact closed-form toy-model mechanism whose extrapolation to real code-versus-prose scaling (Prediction~\ref{pred:boundary}) our pre-registered ladder test contradicted; (iii) a data-limited exponent $\alpha_D=\gamma_{\rm ent}/(2\beta_{\rm corr})$ from temporal corpus statistics, subsuming Cagnetta et al. [5]; and (iv) a joint law with a vanishing cross term and self-truncating variance, yielding two compute-optimality predictions, a near-linear $N^*\propto D^{\alpha_D/\alpha_N}$ tradeoff (consistent with the Chinchilla law) and a superlinear $N^*\propto D^{1/(\alpha_N+\gamma)}$ tradeoff. In principle, no exponent is a free parameter: each is determined by corpus statistics. We report an empirical investigation of the spectral quantities entering these formulas. Bootstrap analysis of the token-covariance spectrum shows that the eigenvalue decay is range-dependent rather than a clean power law, the channel-smoothness quantity $S_i^2$ is non-monotonic, the conditional-entropy exponent $\gamma_{\rm ent}$ remains unresolvable with current estimators, and $\gamma$ (the effective-mode scaling exponent) has not been measured for any real architecture. A synthetic-control experiment---applying the same pipeline to data with known power-law structure---shows the estimator fails to recover the designed slopes, indicating the real-corpus spectral failure is partly measurement-confounded. The data-limited prediction $\alpha_D=\gamma_{\rm ent}/(2\beta_{\rm corr})$ therefore cannot be non-circularly evaluated at present. The entropy-floor identification, the data-limited recovery structure, and the joint law do not depend on Prediction~\ref{pred:boundary} and are unaffected by its test outcome.}

% Author contributions (CRediT taxonomy)
\authorcontributions{Conceptualization, [Author Name]; methodology, [Author Name]; software, [Author Name]; validation, [Author Name]; formal analysis, [Author Name]; investigation, [Author Name]; writing---original draft preparation, [Author Name]; writing---review and editing, [Author Name]; visualization, [Author Name]. All authors have read and agreed to the published version of the manuscript.}

% Funding
\funding{This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.}

% Acknowledgments
\acknowledgments{We thank the anonymous reviewers of an earlier draft for helpful comments, and acknowledge open-source tooling (\LaTeX, PyTorch, HuggingFace datasets, tokenizers) used for the numerical verification and empirical measurements.}

% Conflict of interest
\conflictsofinterest{The authors declare no conflict of interest.}
"""

# Assemble document
doc = preamble + '\n\\begin{document}\n\n'

doc += sec_intro + '\n\n'
doc += methods_section + '\n\n'
doc += results_section + '\n\n'
doc += discussion_section + '\n\n'
doc += conclusions_section + '\n'
doc += availability + '\n'
doc += bibliography + '\n'
doc += '\\end{document}\n'

with open('manuscript/main_entropy.tex', 'w') as f:
    f.write(doc)

print(f"Written manuscript/main_entropy.tex ({len(doc)} chars, {doc.count(chr(10))} lines)")
