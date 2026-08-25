# LaTeX Paper Template

Substitute `${AUTHOR_NAME}` and `${AUTHOR_EMAIL}` from the user (or session
env). Use a placeholder affiliation the user confirms — never paste a
hard-coded personal postal address or email into generated files.

## PRF / Phys. Rev. Fluids

```tex
\documentclass[
reprint,
amsmath,amssymb,
superscriptaddress,
aps,prfluids
]{revtex4-2}

\usepackage{bm,graphicx,dcolumn}
\graphicspath{{figures/}}

\begin{document}

\preprint{APS/123-QED}

\title{Paper Title}

\author{${AUTHOR_NAME}}
\email[]{${AUTHOR_EMAIL}}
\affiliation{%
Department / Lab, Institution, City, Country.
}%

% Add coauthors below.
% \author{Coauthor Name}
% \affiliation{Affiliation goes here}

\date{\today}
```

## PRL / Phys. Rev. Letters

```tex
\documentclass[
reprint,
amsmath,amssymb,
superscriptaddress,
aps,prl
]{revtex4-2}

\usepackage{bm,graphicx,dcolumn}
\graphicspath{{figures/}}

\begin{document}

\preprint{APS/123-QED}

\title{Paper Title}

\author{${AUTHOR_NAME}}
\email[]{${AUTHOR_EMAIL}}
\affiliation{%
Department / Lab, Institution, City, Country.
}%

% Add coauthors below.
% \author{Coauthor Name}
% \affiliation{Affiliation goes here}

\date{\today}
```

## Notes

- Confirm author name, email, and affiliation with the user before writing
  files.
- Add further affiliations only when the work belongs there.
- If a draft wants a preprint look, switch to `preprint` only for the draft, not the submission template.
- Pair this with `paperctl.sh` for build/check/clean flows.
