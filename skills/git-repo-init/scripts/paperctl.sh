#!/bin/bash

# Hybrid paper workflow helper: use Makefile when present, otherwise
# fall back to the standalone compile/check scripts.

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

make_has_target() {
  local target="$1"
  [ -f Makefile ] && grep -Eq "^[[:space:]]*${target}:" Makefile
}

clean_fallback() {
  local texfile="${1:-}"
  if [ -z "$texfile" ]; then
    texfile=$(ls *.tex 2>/dev/null | head -n 1 || true)
  fi
  if [ -z "$texfile" ]; then
    echo "No .tex files found for fallback clean." >&2
    return 1
  fi

  local basename="${texfile%.tex}"
  if command -v latexmk >/dev/null 2>&1; then
    latexmk -C "$texfile" >/dev/null 2>&1 || true
  fi
  rm -f "${basename}.aux" "${basename}.bbl" "${basename}.blg" \
        "${basename}.fdb_latexmk" "${basename}.fls" "${basename}.log" \
        "${basename}.out" "${basename}.toc" "${basename}.lof" \
        "${basename}.lot" "${basename}.nav" "${basename}.snm" \
        "${basename}.vrb" "${basename}.bcf" "${basename}.run.xml" \
        "${basename}.synctex.gz"
  rm -rf build
}

usage() {
  cat <<'EOF'
Usage: ./scripts/paperctl.sh <build|check|clean|help> [texfile]

Commands:
  build   Prefer Makefile, otherwise run ./scripts/compile_tex.sh
  check   Prefer Makefile check-citations, otherwise run ./scripts/check_citations.sh
  clean   Prefer Makefile clean, otherwise remove aux files/build dir
  help    Show this help
EOF
}

cmd="${1:-help}"
texfile="${2:-}"

case "$cmd" in
  build|compile|all)
    if [ -f Makefile ]; then
      make
    elif [ -x "$SCRIPT_DIR/compile_tex.sh" ]; then
      "$SCRIPT_DIR/compile_tex.sh" ${texfile:+"$texfile"}
    else
      echo "No Makefile or compile_tex.sh found." >&2
      exit 1
    fi
    ;;
  check|citations)
    if [ -f Makefile ] && make_has_target check-citations; then
      make check-citations
    elif [ -x "$SCRIPT_DIR/check_citations.sh" ]; then
      "$SCRIPT_DIR/check_citations.sh" ${texfile:+"$texfile"}
    else
      echo "No Makefile check-citations target or check_citations.sh found." >&2
      exit 1
    fi
    ;;
  clean)
    if [ -f Makefile ] && make_has_target clean; then
      make clean
    else
      clean_fallback "$texfile"
    fi
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac
