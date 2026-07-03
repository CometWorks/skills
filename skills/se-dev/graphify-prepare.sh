#!/usr/bin/env bash

# Shared optional Graphify integration for se-dev-* prepare scripts.
# Source this after common-posix.sh so the caller provides log().

se_dev_graphify_print_install_hint() {
    log "Graphify is highly recommended for navigable maps of prepared se-dev corpora."
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
    if [ "${SE_DEV_GRAPHIFY:-1}" = "0" ]; then
        log "Graphify disabled by SE_DEV_GRAPHIFY=0"
        return 1
    fi

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

se_dev_graphify_prepare() {
    local label="$1"
    local root="$2"

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
    if [ -f "$root/graphify-out/graph.json" ]; then
        log "Graphify: updating $label graph at $root"
        graphify "$root" --update || log "WARNING: Graphify update failed for $label; prepare continues."
    else
        log "Graphify: building $label graph at $root"
        graphify "$root" || log "WARNING: Graphify build failed for $label; prepare continues."
    fi
}
