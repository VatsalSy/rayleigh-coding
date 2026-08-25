#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

# Script to check for missing BibTeX citations
# Finds all citation keys used in .tex file and checks if they exist in .bib file

set -o pipefail

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the .tex file from command line argument or auto-detect
if [ -n "$1" ]; then
    TEXFILE="$1"
else
    # Auto-detect: find all .tex files
    tex_files=(*.tex)
    if [ ! -f "${tex_files[0]}" ]; then
        echo -e "${RED}Error: No .tex files found in current directory${NC}"
        exit 1
    fi
    # Use first .tex file found
    TEXFILE="${tex_files[0]}"
fi

# Check if .tex file exists
if [ ! -f "$TEXFILE" ]; then
    echo -e "${RED}Error: $TEXFILE not found${NC}"
    exit 1
fi

echo "Citation Checker for LaTeX"
echo "==========================="
echo "Analyzing: $TEXFILE"

# Step 1: Extract all citation keys from .tex file
echo ""
echo "Step 1: Extracting citation keys from .tex file..."

# Match \cite, \citep, \citet, \citeauthor, \citeyear, etc.
# Strip LaTeX comments to avoid matching commented cites, allow optional
# starred forms and bracketed arguments, then extract keys.
cite_keys=$(perl -pe 's/(?<!\\)%.*//' "$TEXFILE" | \
            grep -oE '\\cite[a-zA-Z]*(\*)?(\[[^]]*\])*\{[^}]+\}' | \
            sed -E 's/\\cite[a-zA-Z]*(\*)?(\[[^]]*\])*\{//g' | \
            sed 's/}//g' | \
            tr ',' '\n' | \
            sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | \
            sort -u)

if [ -z "$cite_keys" ]; then
    echo -e "${YELLOW}No citation keys found in .tex file${NC}"
    exit 0
fi

cite_count=$(echo "$cite_keys" | wc -l | tr -d ' ')
echo -e "${GREEN}Found $cite_count unique citation keys${NC}"

# Step 2: Find .bib file(s) from .tex file
echo ""
echo "Step 2: Finding .bib file(s) from .tex file..."

bib_lines=$(perl -pe 's/(?<!\\)%.*//' "$TEXFILE" | \
            grep -oE '\\bibliography\{[^}]+\}|\\addbibresource(\[[^]]*\])?\{[^}]+\}')

if [ -z "$bib_lines" ]; then
    echo -e "${RED}Error: No \\bibliography{} or \\addbibresource{} command found in $TEXFILE${NC}"
    exit 1
fi

bib_files=()
while IFS= read -r line; do
    value=${line#*\{}
    value=${value%\}}
    IFS=',' read -r -a parts <<< "$value"
    for part in "${parts[@]}"; do
        trimmed=$(echo "$part" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')
        [ -z "$trimmed" ] && continue
        [[ "$trimmed" =~ \.bib$ ]] || trimmed="${trimmed}.bib"
        bib_files+=("$trimmed")
    done
done <<< "$bib_lines"

if [ ${#bib_files[@]} -eq 0 ]; then
    echo -e "${RED}Error: No bibliography files resolved from $TEXFILE${NC}"
    exit 1
fi

# Deduplicate while preserving order
unique_bib_files=()
for bf in "${bib_files[@]}"; do
    skip=false
    for existing in "${unique_bib_files[@]}"; do
        if [ "$existing" = "$bf" ]; then
            skip=true
            break
        fi
    done
    if [ "$skip" = false ]; then
        unique_bib_files+=("$bf")
    fi
done
bib_files=("${unique_bib_files[@]}")

for bf in "${bib_files[@]}"; do
    if [ ! -f "$bf" ]; then
        echo -e "${RED}Error: Bibliography file $bf not found${NC}"
        exit 1
    fi
done

echo -e "${GREEN}Found bibliography file(s): ${bib_files[*]}${NC}"

# Step 3: Extract citation keys from .bib file(s)
echo ""
echo "Step 3: Extracting citation keys from .bib file(s)..."

# Match @article{key, @book{key, etc.
bib_keys=$(
    for bf in "${bib_files[@]}"; do
        grep -oE '@[a-zA-Z]+\{[^,]+,' "$bf"
    done | \
    sed 's/@[a-zA-Z]*{//g' | \
    sed 's/,//g' | \
    sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | \
    sort -u
)

if [ -z "$bib_keys" ]; then
    echo -e "${RED}Error: No entries found in ${bib_files[*]}${NC}"
    exit 1
fi

bib_count=$(echo "$bib_keys" | wc -l | tr -d ' ')
echo -e "${GREEN}Found $bib_count entries across ${#bib_files[@]} bibliography file(s)${NC}"

# Step 4: Find missing keys
echo ""
echo "Step 4: Checking for missing citations..."

missing_keys=""
for key in $cite_keys; do
    if ! echo "$bib_keys" | grep -qx "$key"; then
        missing_keys="$missing_keys"$'\n'"$key"
    fi
done

missing_keys=$(echo "$missing_keys" | grep -v '^$')

# Report results
echo ""
echo "Results:"
echo "========"
if [ -z "$missing_keys" ]; then
    echo -e "${GREEN}✓ All cited keys are present in ${bib_files[*]}${NC}"
    echo ""
    echo "Summary:"
    echo "  Citations in .tex: $cite_count"
    echo "  Entries in .bib:   $bib_count"
    exit 0
else
    missing_count=$(echo "$missing_keys" | wc -l | tr -d ' ')
    echo -e "${RED}✗ Found $missing_count missing citation(s):${NC}"
    echo ""
    echo "$missing_keys" | while read -r key; do
        echo -e "${RED}  - $key${NC}"
    done
    echo ""
    echo "Summary:"
    echo "  Citations in .tex: $cite_count"
    echo "  Entries in .bib:   $bib_count"
    echo "  Missing:           $missing_count"
    exit 1
fi
