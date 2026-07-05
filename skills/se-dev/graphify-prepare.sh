#!/usr/bin/env bash

# Shared optional Graphify integration for se-dev-* prepare scripts.
# Source this after common-posix.sh so the caller provides log().
#
# Graphify is STRICTLY OPTIONAL and OFF by default. Building the graph for the
# large decompiled game/server corpora can take ~10-30 minutes on top of the
# normal prepare time, so it is only built when the user explicitly opts in by
# exporting SE_DEV_GRAPHIFY=1 before running prepare.

# True only when the user explicitly opted in with SE_DEV_GRAPHIFY=1.
se_dev_graphify_enabled() {
    [ "${SE_DEV_GRAPHIFY:-0}" = "1" ]
}

se_dev_graphify_print_install_hint() {
    log "Graphify builds a navigable map beside the regular search indexes."
    log "Install options:"
    log "  uv tool install graphifyy"
    log "  pipx install graphifyy"
    log "  pip install graphifyy"
    log "Then wire it into your AI platform:"
    log "  graphify install --platform [AI PLATFORM]"
}

se_dev_graphify_install_package() {
    if command -v uv >/dev/null 2>&1; then
        uv tool install graphifyy
    elif command -v pipx >/dev/null 2>&1; then
        pipx install graphifyy
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m pip install graphifyy
    else
        log "WARNING: Could not install Graphify automatically; missing uv, pipx, and python3."
        return 1
    fi
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

# Classify the state of a graph under <root>/graphify-out. Echoes one of:
#   missing     - no graph.json (never built or failed early)
#   incomplete  - graph.json present but clustering data (.graphify_analysis.json)
#                 is absent or graph.json is implausibly small (build interrupted
#                 or clustering never finished; the graph is unusable)
#   ok          - graph.json plus clustering data present
se_dev_graphify_status() {
    local root="$1"
    local out="$root/graphify-out"
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

# du -sk that tolerates a missing path (echoes 0).
se_dev_graphify_du_kb() {
    local path="$1"
    [ -e "$path" ] || { printf '0\n'; return 0; }
    du -sk "$path" 2>/dev/null | awk '{print $1; exit}'
}

# Estimate the free space (KiB) a graph build needs under <root>. Measured on
# the decompiled game/server corpora, the graph output (graph.json + clustering
# + semantic cache) runs ~9x the source size (e.g. ~1.5 GiB of output for a
# ~175 MiB corpus). We require 12x the corpus plus a fixed 1 GiB of headroom,
# which covers the observed footprint with margin and room for the code base to
# grow. The corpus size excludes any existing graphify-out so re-runs are not
# double-counted.
se_dev_graphify_required_kb() {
    local root="$1"
    local total_kb out_kb corpus_kb
    total_kb="$(se_dev_graphify_du_kb "$root")"
    out_kb="$(se_dev_graphify_du_kb "$root/graphify-out")"
    corpus_kb=$(( total_kb - out_kb ))
    [ "$corpus_kb" -ge 0 ] 2>/dev/null || corpus_kb=0
    printf '%s\n' "$(( corpus_kb * 12 + 1048576 ))"
}

# Free space (KiB) on the filesystem that holds <root>.
se_dev_graphify_avail_kb() {
    df -Pk "$1" 2>/dev/null | awk 'NR==2 {print $4; exit}'
}

# Pre-check: is there enough disk for the graph build? Returns non-zero (and
# logs how much is short) when there is not. Graphify is optional, so callers
# skip the build rather than fail the whole prepare.
se_dev_graphify_check_disk() {
    local label="$1" root="$2"
    local need avail
    need="$(se_dev_graphify_required_kb "$root")"
    avail="$(se_dev_graphify_avail_kb "$root")"

    if [ -z "$avail" ]; then
        log "Graphify: could not determine free disk space for $label; proceeding without a disk pre-check."
        return 0
    fi

    if [ "$avail" -lt "$need" ]; then
        log "Graphify: skipping $label - not enough free disk space for the graph."
        log "  Needed (graph + cache + 1 GiB headroom): ~$(( need / 1024 )) MB"
        log "  Available on the graph volume:           ~$(( avail / 1024 )) MB"
        log "  Free up space, then re-run prepare with SE_DEV_GRAPHIFY=1. Core prepare already succeeded."
        return 1
    fi

    log "Graphify: disk pre-check OK for $label (need ~$(( need / 1024 )) MB, have ~$(( avail / 1024 )) MB)"
    return 0
}

# Remove a graph directory so it can be rebuilt from scratch.
se_dev_graphify_clean() {
    local root="$1"
    local out="$root/graphify-out"
    if [ -d "$out" ]; then
        log "Graphify: removing unusable graph at $out"
        rm -rf "$out"
    fi
}

se_dev_graphify_prepare() {
    local label="$1"
    local root="$2"

    if ! se_dev_graphify_enabled; then
        log "Graphify: skipping $label (set SE_DEV_GRAPHIFY=1 to build the optional graph)"
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

    se_dev_graphify_ensure_available || return 0

    root="$(cd -P -- "$root" && pwd)"

    se_dev_graphify_check_disk "$label" "$root" || return 0

    local status
    status="$(se_dev_graphify_status "$root")"
    case "$status" in
        ok)
            log "Graphify: updating $label graph at $root"
            graphify "$root" --update || log "WARNING: Graphify update failed for $label; prepare continues."
            ;;
        incomplete)
            log "Graphify: $label graph is incomplete (clustering missing or interrupted); rebuilding from scratch"
            se_dev_graphify_clean "$root"
            graphify "$root" || log "WARNING: Graphify build failed for $label; prepare continues."
            ;;
        *)
            log "Graphify: building $label graph at $root"
            graphify "$root" || log "WARNING: Graphify build failed for $label; prepare continues."
            ;;
    esac
}
