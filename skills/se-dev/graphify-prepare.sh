#!/usr/bin/env bash

# Shared Graphify integration for se-dev-* prepare scripts.
# Source this after common-posix.sh so the caller provides log().
#
# Clustering (community detection) is the slow part of a Graphify build. Graphify
# has two backends for it:
#   * fast: native Rust Leiden via graspologic — needs Python < 3.13 (we use 3.12).
#   * slow: pure-Python Louvain fallback — single core, ~10-30 min on the ~220k-node
#           game/server graphs. Used automatically when graspologic is not importable
#           (e.g. Graphify installed on Python 3.13, where graspologic has no wheel).
#
# So we default the Graphify tool to Python 3.12 with the `leiden` extra. When the
# fast Rust backend is available prepare builds the graph AUTOMATICALLY; when it can
# not be provisioned (no uv / no Python 3.12) Graphify stays OPTIONAL and off unless
# the user opts in with SE_DEV_GRAPHIFY=1, and prepare reports the extra time it costs.
#
# SE_DEV_GRAPHIFY is tri-state:
#   unset -> auto: build when the fast Rust backend is available, skip otherwise
#   1     -> always build (even on the slow single-core fallback)
#   0     -> never build

# Python version the Graphify tool runs under. Fast clustering (graspologic's Rust
# Leiden) needs Python < 3.13; 3.13 silently drops to the slow fallback. Override
# with SE_DEV_GRAPHIFY_PYTHON if 3.12 is unsuitable on a given machine.
SE_DEV_GRAPHIFY_PYTHON="${SE_DEV_GRAPHIFY_PYTHON:-3.12}"

# Set by se_dev_graphify_provision(): "fast" or "slow".
SE_DEV_GRAPHIFY_SPEED="slow"

# Environment variables Graphify auto-detects an LLM backend from. Without one of
# these it refuses to extract doc/paper/image files and the whole build fails, even
# though the code was already indexed locally by the AST extractor.
SE_DEV_GRAPHIFY_API_KEY_VARS="GEMINI_API_KEY GOOGLE_API_KEY MOONSHOT_API_KEY ANTHROPIC_API_KEY OPENAI_API_KEY DEEPSEEK_API_KEY"

# The decompiled game/server-code graph.json is well over Graphify's default 512 MB
# load cap, which would abort every build and update. Raise it, but let an explicitly
# set value win so a larger corpus can be accommodated without editing this file.
export GRAPHIFY_MAX_GRAPH_BYTES="${GRAPHIFY_MAX_GRAPH_BYTES:-2GB}"

se_dev_graphify_opt_in()  { [ "${SE_DEV_GRAPHIFY:-}" = "1" ]; }
se_dev_graphify_opt_out() { [ "${SE_DEV_GRAPHIFY:-}" = "0" ]; }

# True when no LLM API key is configured. Checked with indirect expansion so an
# empty value counts as unset, which is how Graphify itself treats it.
se_dev_graphify_no_api_key() {
    local name
    for name in $SE_DEV_GRAPHIFY_API_KEY_VARS; do
        [ -n "${!name:-}" ] && return 1
    done
    return 0
}

# Echo --code-only when the semantic extraction pass cannot run, so a corpus that
# mixes code with docs or images still produces a code graph instead of failing.
# Graphify aborts the entire build on the first doc/paper/image file it cannot send
# to an LLM, which killed the graph for every skill whose sources carry a README or
# a screenshot. SE_DEV_GRAPHIFY_CODE_ONLY overrides the detection:
#   unset -> auto: code-only when no API key is configured, full extraction otherwise
#   1     -> always code-only (fast, deterministic, no LLM calls)
#   0     -> never: keep semantic extraction even with no key detected, for a
#            keyless backend such as a local ollama passed through --backend
se_dev_graphify_code_only() {
    case "${SE_DEV_GRAPHIFY_CODE_ONLY:-}" in
        1) return 0 ;;
        0) return 1 ;;
    esac
    se_dev_graphify_no_api_key
}

se_dev_graphify_print_install_hint() {
    log "Graphify builds a navigable map beside the regular search indexes."
    log "Fast clustering needs the native Rust Leiden backend (graspologic on Python ${SE_DEV_GRAPHIFY_PYTHON})."
    log "Install options:"
    log "  uv tool install --python ${SE_DEV_GRAPHIFY_PYTHON} 'graphifyy[leiden]'   # recommended (fast backend)"
    log "  pipx install --python python${SE_DEV_GRAPHIFY_PYTHON} 'graphifyy[leiden]'"
    log "  pip install 'graphifyy[leiden]'                        # only fast on Python ${SE_DEV_GRAPHIFY_PYTHON}"
    log "Then wire it into your AI platform:"
    log "  graphify install --platform [AI PLATFORM]"
}

# Install Graphify, preferring the fast native Rust Leiden backend (Python 3.12 +
# the `leiden` extra). Falls back to a plain install (slow clustering) when the
# fast backend cannot be arranged.
se_dev_graphify_install_package() {
    if command -v uv >/dev/null 2>&1; then
        # uv auto-downloads CPython 3.12 when it is not already present.
        if uv tool install --python "$SE_DEV_GRAPHIFY_PYTHON" --force "graphifyy[leiden]"; then
            return 0
        fi
        log "WARNING: installing graphifyy[leiden] on Python $SE_DEV_GRAPHIFY_PYTHON failed; retrying without the fast backend."
        uv tool install --force graphifyy
        return
    fi

    local py312
    py312="$(command -v "python$SE_DEV_GRAPHIFY_PYTHON" 2>/dev/null || true)"

    if command -v pipx >/dev/null 2>&1; then
        if [ -n "$py312" ]; then
            pipx install --python "$py312" "graphifyy[leiden]" && return 0
            log "WARNING: pipx install of graphifyy[leiden] failed; retrying without the fast backend."
        else
            log "python$SE_DEV_GRAPHIFY_PYTHON not found; the fast Rust clustering backend needs it. Installing without it (clustering will use the slow fallback)."
        fi
        pipx install graphifyy
        return
    fi

    if [ -n "$py312" ]; then
        "$py312" -m pip install "graphifyy[leiden]" && return 0
        log "WARNING: pip install of graphifyy[leiden] on $py312 failed; retrying without the fast backend."
    fi
    if command -v python3 >/dev/null 2>&1; then
        log "python$SE_DEV_GRAPHIFY_PYTHON not found; installing Graphify without the fast Rust backend (clustering will use the slow fallback)."
        python3 -m pip install graphifyy
        return
    fi

    log "WARNING: Could not install Graphify automatically; missing uv, pipx, and python3."
    return 1
}

se_dev_graphify_install_platform() {
    if [ -n "${SE_DEV_GRAPHIFY_PLATFORM:-}" ]; then
        graphify install --platform "$SE_DEV_GRAPHIFY_PLATFORM" || log "WARNING: graphify platform install failed for '$SE_DEV_GRAPHIFY_PLATFORM'."
        return 0
    fi

    if [ -r /dev/tty ] && [ -w /dev/tty ]; then
        local platform
        printf 'Enter Graphify AI platform for `graphify install --platform`, or press Enter to skip: ' >/dev/tty
        IFS= read -r platform </dev/tty || platform=""
        if [ -n "$platform" ]; then
            graphify install --platform "$platform" || log "WARNING: graphify platform install failed for '$platform'."
            return 0
        fi
    fi

    log "Graphify package installed. To wire it into your AI platform later, run:"
    log "  graphify install --platform [AI PLATFORM]"
}

# Interactive install path used only when the fast backend is unavailable and the
# user opted in with SE_DEV_GRAPHIFY=1. The fast path installs non-interactively in
# se_dev_graphify_provision().
se_dev_graphify_ensure_available() {
    if command -v graphify >/dev/null 2>&1; then
        return 0
    fi

    se_dev_graphify_print_install_hint

    if [ ! -r /dev/tty ] || [ ! -w /dev/tty ]; then
        log "Graphify not installed and no interactive terminal is available; skipping graph build."
        return 1
    fi

    local answer
    printf 'Install Graphify now? [y/N] ' >/dev/tty
    IFS= read -r answer </dev/tty || answer=""
    case "$answer" in
        y|Y|yes|YES)
            se_dev_graphify_install_package || return 1
            ;;
        *)
            log "Graphify install declined; skipping graph build."
            return 1
            ;;
    esac

    if command -v graphify >/dev/null 2>&1; then
        se_dev_graphify_install_platform
        return 0
    fi

    log "WARNING: Graphify install completed but graphify is still not on PATH; skipping graph build."
    return 1
}

# Path to the Python interpreter the installed Graphify tool runs under, or empty.
# Reads the launcher shebang so it works for uv/pipx/pip installs alike.
se_dev_graphify_tool_python() {
    local gf line py
    gf="$(command -v graphify 2>/dev/null)" || return 1
    [ -n "$gf" ] || return 1
    line="$(head -n 1 "$gf" 2>/dev/null)"
    case "$line" in
        '#!'*) ;;
        *) return 1 ;;
    esac
    py="${line#\#!}"
    py="${py%$'\r'}"                 # tolerate CRLF launchers
    case "$py" in
        *' '*)                       # "/usr/bin/env python3" or "python -x"
            py="${py##* }"
            command -v "$py" 2>/dev/null
            return
            ;;
    esac
    printf '%s\n' "$py"
}

# 0 when the Graphify tool can run the fast native Rust Leiden backend.
se_dev_graphify_leiden_available() {
    local py
    py="$(se_dev_graphify_tool_python)" || return 1
    [ -n "$py" ] && [ -x "$py" ] || return 1
    "$py" -c "import graspologic.partition" >/dev/null 2>&1
}

# Make the fast Rust Leiden backend available when we can do so non-interactively
# (uv present). Sets SE_DEV_GRAPHIFY_SPEED to "fast" or "slow". Never fails the run.
se_dev_graphify_provision() {
    SE_DEV_GRAPHIFY_SPEED="slow"

    # Put uv's tool bin dir on PATH so a freshly-installed graphify is visible in
    # this same shell (a first-time `uv tool install` otherwise needs a new shell).
    if command -v uv >/dev/null 2>&1; then
        local bin
        bin="$(uv tool dir --bin 2>/dev/null || true)"
        if [ -n "$bin" ]; then
            case ":$PATH:" in
                *":$bin:"*) ;;
                *) PATH="$bin:$PATH"; export PATH ;;
            esac
        fi
    fi

    if se_dev_graphify_leiden_available; then
        SE_DEV_GRAPHIFY_SPEED="fast"
        return 0
    fi

    # Only uv can pin Graphify to Python 3.12 non-interactively (auto-fetching it
    # if needed). Without uv we cannot guarantee the fast backend here.
    if ! command -v uv >/dev/null 2>&1; then
        return 0
    fi

    log "Graphify: provisioning the fast Rust clustering backend (uv + Python ${SE_DEV_GRAPHIFY_PYTHON}; one-time ~30-60s)..."
    if uv tool install --python "$SE_DEV_GRAPHIFY_PYTHON" --force "graphifyy[leiden]" >/dev/null 2>&1; then
        if [ -n "${SE_DEV_GRAPHIFY_PLATFORM:-}" ]; then
            graphify install --platform "$SE_DEV_GRAPHIFY_PLATFORM" >/dev/null 2>&1 \
                || log "WARNING: graphify platform install failed for '$SE_DEV_GRAPHIFY_PLATFORM'."
        fi
    else
        log "WARNING: could not provision the fast Rust backend automatically; will use the slow fallback."
    fi

    se_dev_graphify_leiden_available && SE_DEV_GRAPHIFY_SPEED="fast"
    return 0
}

# Classify the state of a graph under <out-dir>/graphify-out, where <out-dir>
# defaults to the graphed root. Echoes one of:
#   missing     - no graph.json (never built or failed early)
#   incomplete  - graph.json present but clustering data (.graphify_analysis.json)
#                 is absent or graph.json is implausibly small (build interrupted
#                 or clustering never finished; the graph is unusable)
#   ok          - graph.json plus clustering data present
se_dev_graphify_status() {
    local root="$1"
    local out="${2:-$root}/graphify-out"
    local graph="$out/graph.json"

    if [ ! -f "$graph" ]; then
        printf 'missing\n'
        return 0
    fi

    # A truncated/empty graph.json means the build died mid-write.
    local size
    size="$(wc -c <"$graph" 2>/dev/null | tr -d ' ')"
    if [ -z "$size" ] || [ "$size" -lt 1024 ]; then
        printf 'incomplete\n'
        return 0
    fi

    # Clustering writes .graphify_analysis.json. Without it every node has an
    # empty community and the graph is only half-built.
    if [ ! -f "$out/.graphify_analysis.json" ]; then
        printf 'incomplete\n'
        return 0
    fi

    printf 'ok\n'
}

# Remove a graph directory so it can be rebuilt from scratch.
se_dev_graphify_clean() {
    local root="$1"
    local out="${2:-$root}/graphify-out"
    if [ -d "$out" ]; then
        log "Graphify: removing unusable graph at $out"
        rm -rf "$out"
    fi
}

# Build or update the graph of $root, healing an incomplete (unclustered) graph.
# The graph is written to <out-dir>/graphify-out; <out-dir> defaults to $root, so
# callers that do not pass one keep the graph inside the graphed tree. Callers
# that keep the corpus clean (the code skills) pass the Data folder instead.
se_dev_graphify_run_build() {
    local label="$1"
    local root="$2"
    local outdir="${3:-$2}"
    local status
    status="$(se_dev_graphify_status "$root" "$outdir")"

    # Extra flags for the graphify invocation. --out is passed only when it differs
    # from the root, so the default invocation stays byte-identical to what the
    # other skills have always run.
    #
    # The expansion is guarded rather than plain: callers source this under
    # `set -u`, and bash before 4.4 (RHEL/CentOS 7 ship 4.2) treats an empty
    # array expansion as an unbound variable. The array IS empty for a skill that
    # passes no output directory and has an API key configured, so the graph build
    # would abort on those systems.
    local build_args=()
    if [ "$outdir" != "$root" ]; then
        build_args=(--out "$outdir")
    fi
    if se_dev_graphify_code_only; then
        log "Graphify: indexing $label code only (no LLM API key needed; docs and images are skipped)"
        build_args+=(--code-only)
    fi

    case "$status" in
        ok)
            log "Graphify: updating $label graph of $root at $outdir/graphify-out"
            graphify "$root" --update ${build_args[@]+"${build_args[@]}"} || log "WARNING: Graphify update failed for $label; prepare continues."
            ;;
        incomplete)
            log "Graphify: $label graph is incomplete (clustering missing or interrupted); rebuilding from scratch"
            se_dev_graphify_clean "$root" "$outdir"
            graphify "$root" ${build_args[@]+"${build_args[@]}"} || log "WARNING: Graphify build failed for $label; prepare continues."
            ;;
        *)
            log "Graphify: building $label graph of $root at $outdir/graphify-out"
            graphify "$root" ${build_args[@]+"${build_args[@]}"} || log "WARNING: Graphify build failed for $label; prepare continues."
            ;;
    esac
}

# se_dev_graphify_prepare <label> <root> [out-dir] [source-state]
#
# <root>          the tree to graph
# <out-dir>       where to put graphify-out/ (default: <root>). Pass a directory
#                 outside <root> to keep the graphed tree free of build output.
# <source-state>  "unchanged" when the caller knows nothing under <root> was
#                 regenerated in this run, so an existing healthy graph still
#                 matches its sources and is left untouched. Anything else
#                 (default "changed") builds or updates as before.
se_dev_graphify_prepare() {
    local label="$1"
    local root="$2"
    local outdir="${3:-$2}"
    local source_state="${4:-changed}"

    if se_dev_graphify_opt_out; then
        log "Graphify: skipping $label (SE_DEV_GRAPHIFY=0)"
        return 0
    fi

    if [ -z "$root" ]; then
        log "Graphify: skipping $label (empty root)"
        return 0
    fi

    if [ ! -d "$root" ]; then
        log "Graphify: skipping $label (missing root: $root)"
        return 0
    fi

    # Sources unchanged and the existing graph is usable: there is nothing to do.
    # Checked before provisioning so an up-to-date graph costs neither a tool
    # install nor the disk pre-check scan of the whole corpus.
    if [ "$source_state" = "unchanged" ] && [ "$(se_dev_graphify_status "$root" "$outdir")" = "ok" ]; then
        log "Graphify: $label graph is up to date (sources unchanged); skipping"
        return 0
    fi

    se_dev_graphify_provision

    if [ "$SE_DEV_GRAPHIFY_SPEED" = "fast" ]; then
        log "Graphify: fast native Rust Leiden backend active — building $label automatically."
    elif se_dev_graphify_opt_in; then
        log "Graphify: fast Rust backend unavailable; building $label with the slow single-core fallback (expect ~10-30 min for the game/server corpora)."
        se_dev_graphify_ensure_available || return 0
    else
        log "Graphify: skipping $label — the fast Rust clustering backend is unavailable (needs uv + Python ${SE_DEV_GRAPHIFY_PYTHON})."
        log "Building now would use the slow single-core fallback (~10-30 min for the game/server corpora). Set SE_DEV_GRAPHIFY=1 to build anyway."
        return 0
    fi

    root="$(cd -P -- "$root" && pwd)"
    mkdir -p "$outdir" || {
        log "Graphify: skipping $label (cannot create output directory: $outdir)"
        return 0
    }
    outdir="$(cd -P -- "$outdir" && pwd)"
    se_dev_graphify_run_build "$label" "$root" "$outdir"
}
