#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

# Script to compile LaTeX files using latexmk and clean aux files
# Preserves PDFs and .synctex.gz files
#
# Usage: ./compile_tex.sh [-y|--yes] [texfile]
#
# Options:
#   -y, --yes    Non-interactive mode: auto-continue on missing citations
#
# Environment Variables:
#   CI=1         Enable non-interactive mode (for CI/CD pipelines)
#   FORCE_YES=1  Enable non-interactive mode (alternative to CI)
#
# Examples:
#   ./compile_tex.sh                    # Interactive mode, compile all .tex files
#   ./compile_tex.sh paper.tex          # Interactive mode, compile specific file
#   ./compile_tex.sh -y                 # Non-interactive, compile all files
#   ./compile_tex.sh --yes paper.tex    # Non-interactive, compile specific file
#   CI=1 ./compile_tex.sh               # CI mode, auto-continue on warnings

set -o pipefail

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo -e "${RED}Error: required command '$1' not found in PATH${NC}" >&2
    exit 127
  }
}

# Ensure latexmk is available
need_cmd latexmk

# Parse command-line arguments
AUTO_YES=0
TEXFILE_ARG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes)
            AUTO_YES=1
            shift
            ;;
        -*)
            echo -e "${RED}Error: Unknown option: $1${NC}" >&2
            echo "Usage: $0 [-y|--yes] [texfile]" >&2
            exit 1
            ;;
        *)
            TEXFILE_ARG="$1"
            shift
            ;;
    esac
done

# Check environment variables for non-interactive mode
if [[ "${CI:-0}" == "1" ]] || [[ "${FORCE_YES:-0}" == "1" ]]; then
    AUTO_YES=1
fi

# Function to compile a tex file with latexmk
compile_tex() {
    local texfile=$1
    echo -e "${GREEN}Compiling ${texfile} with latexmk...${NC}"
    latexmk -pdf -bibtex -synctex=1 -f "${texfile}"
}

# Function to clean aux files via latexmk (keeps PDF and synctex)
clean_tex() {
    local texfile=$1
    local basename="${texfile%.tex}"
    echo "Cleaning aux files for ${texfile} (keeping PDF and synctex)..."
    latexmk -c "${texfile}"

    # Explicitly remove additional temporary files
    echo "Removing additional temporary files: ${basename}.*"
    rm -fv "${basename}.aux" "${basename}.bbl" "${basename}.blg" \
          "${basename}.fdb_latexmk" "${basename}.fls" "${basename}.log" \
          "${basename}.out" "${basename}.toc" "${basename}.lof" \
          "${basename}.lot" "${basename}.nav" "${basename}.snm" \
          "${basename}.vrb" 2>/dev/null || true
    echo "Cleanup complete for ${basename}"
}

# Function to get tex files to compile
get_tex_files() {
    local specified_file="$1"

    # If file specified as argument, use only that file
    if [ -n "$specified_file" ]; then
        if [ -f "$specified_file" ]; then
            printf '%s\n' "$specified_file"
            return 0
        else
            echo -e "${RED}Error: Specified file '$specified_file' not found${NC}" >&2
            exit 1
        fi
    fi

    # Find all .tex files in current directory
    local tex_files=(*.tex)

    # Check if any .tex files exist
    if [ ! -f "${tex_files[0]}" ]; then
        echo -e "${RED}Error: No .tex files found in current directory${NC}" >&2
        exit 1
    fi

    # Return all .tex files, one per line
    printf '%s\n' "${tex_files[@]}"
}

echo "LaTeX Compilation Script (latexmk)"
echo "=================================="
echo ""

# Get list of files to compile
TEX_FILES=()
while IFS= read -r line; do
    TEX_FILES+=("$line")
done < <(get_tex_files "$TEXFILE_ARG")
echo -e "${GREEN}Found ${#TEX_FILES[@]} .tex file(s) to compile${NC}"
for f in "${TEX_FILES[@]}"; do
    echo "  - $f"
done
echo ""

# Check for missing citations first (for all files to be compiled)
if [ -f "$SCRIPT_DIR/check_citations.sh" ]; then
    citation_failed=0
    for TEXFILE in "${TEX_FILES[@]}"; do
        if ! bash "$SCRIPT_DIR/check_citations.sh" "$TEXFILE"; then
            citation_failed=1
        fi
        echo ""
    done

    if [ $citation_failed -ne 0 ]; then
        echo -e "${RED}Missing citations detected in one or more files!${NC}"

        if [ $AUTO_YES -eq 1 ]; then
            # Non-interactive mode: auto-continue
            echo -e "${GREEN}Non-interactive mode: continuing with compilation...${NC}"
        else
            # Interactive mode: prompt user
            read -p "Do you want to continue with compilation anyway? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Compilation cancelled. Please fix missing citations first."
                exit 1
            fi
            echo -e "${GREEN}Continuing with compilation...${NC}"
        fi
    fi
    echo ""
fi

# Track overall compilation status
overall_status=0

# Compile each file
for TEXFILE in "${TEX_FILES[@]}"; do
    echo ""
    echo "========================================="
    compile_tex "$TEXFILE"
    file_status=$?

    if [ $file_status -ne 0 ]; then
        overall_status=1
    fi

    # Clean aux files
    echo ""
    echo "Cleaning temporary files for $TEXFILE..."
    clean_tex "$TEXFILE"
    echo "========================================="

    # Summary for this file
    PDFFILE="${TEXFILE%.tex}.pdf"
    if [ $file_status -eq 0 ]; then
        echo -e "${GREEN}✓ $PDFFILE compiled successfully${NC}"
    else
        echo -e "${RED}✗ $PDFFILE compilation failed${NC}"
    fi
done

# Overall summary
echo ""
echo "Compilation Complete"
echo "===================="

echo ""
echo "Preserved files: PDFs and .synctex.gz (via latexmk -c)"

# Exit with error if any compilation failed
if [ $overall_status -ne 0 ]; then
    exit 1
fi

exit 0
