#!/usr/bin/env bash

SE_APP_ID=244850
ILSPY_VERSION="${ILSPY_VERSION:-10.0.1.8346}"
SE_TOOLS_ROOT="${SE_TOOLS_ROOT:-$HOME/.se-dev/tools}"

log() {
    printf '%s\n' "$*"
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

resolve_script_dir() {
    local source_path="${BASH_SOURCE[0]}"
    while [ -L "$source_path" ]; do
        local dir
        dir="$(cd -P -- "$(dirname -- "$source_path")" && pwd)"
        source_path="$(readlink "$source_path")"
        case "$source_path" in
            /*) ;;
            *) source_path="$dir/$source_path" ;;
        esac
    done
    cd -P -- "$(dirname -- "$source_path")" && pwd
}

prepend_user_paths() {
    case ":$PATH:" in
        *":$HOME/.local/bin:"*) ;;
        *) PATH="$HOME/.local/bin:$PATH" ;;
    esac
    case ":$PATH:" in
        *":$HOME/.cargo/bin:"*) ;;
        *) PATH="$HOME/.cargo/bin:$PATH" ;;
    esac
    case ":$PATH:" in
        *":$HOME/.dotnet/tools:"*) ;;
        *) PATH="$HOME/.dotnet/tools:$PATH" ;;
    esac
    export PATH
}

find_python() {
    local candidate
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done
    return 1
}

require_python_3_11() {
    prepend_user_paths
    PYTHON_BIN="${PYTHON_BIN:-$(find_python 2>/dev/null || true)}"
    [ -n "${PYTHON_BIN:-}" ] || fail "Missing Python. Install Python 3.11 or newer."
    "$PYTHON_BIN" - <<'PY' || fail "Python 3.11 or newer required."
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PY
    export PYTHON_BIN
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || fail "Missing $1."
}

ensure_uv() {
    prepend_user_paths
    if command -v uv >/dev/null 2>&1; then
        return 0
    fi

    log "Installing uv"
    if command -v curl >/dev/null 2>&1; then
        curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
    else
        fail "Missing uv and neither curl nor wget is available to install it."
    fi

    prepend_user_paths
    command -v uv >/dev/null 2>&1 || fail "uv installation finished but uv is still not on PATH."
}

ensure_uv_sync() {
    if [ -d .venv ]; then
        return 0
    fi
    log "Setting up Python .venv (uv sync)"
    uv sync
}

default_data_home() {
    printf '%s\n' "${SE_DEV_DATA_ROOT:-$HOME/.se-dev}"
}

ensure_directory_link() {
    local link_path="$1"
    local target_path="$2"
    mkdir -p "$target_path"
    if [ -L "$link_path" ] || [ -e "$link_path" ]; then
        return 0
    fi
    ln -s "$target_path" "$link_path"
}

ensure_temp_link() {
    local link_path="$1"
    local target_path="$2"
    if [ -e "$link_path" ] && [ ! -L "$link_path" ]; then
        fail "$link_path exists and is not a symlink. Remove it or point it at $target_path."
    fi
    if [ -L "$link_path" ]; then
        return 0
    fi
    ln -s "$target_path" "$link_path"
}

steamapps_candidates() {
    if [ -n "${STEAMAPPS_DIR:-}" ]; then
        printf '%s\n' "$STEAMAPPS_DIR"
    fi

    printf '%s\n' \
        "$HOME/.local/share/Steam/steamapps" \
        "$HOME/.steam/steam/steamapps" \
        "$HOME/.steam/root/steamapps" \
        "$HOME/.steam/debian-installation/steamapps" \
        "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps" \
        "$HOME/Library/Application Support/Steam/steamapps"
}

detect_game_root() {
    if [ -n "${SE_GAME_ROOT:-}" ]; then
        [ -d "$SE_GAME_ROOT" ] || fail "SE_GAME_ROOT does not exist: $SE_GAME_ROOT"
        printf '%s\n' "$SE_GAME_ROOT"
        return 0
    fi

    local steamapps
    while IFS= read -r steamapps; do
        [ -d "$steamapps" ] || continue
        local candidate="$steamapps/common/SpaceEngineers"
        if [ -d "$candidate" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done <<EOF
$(steamapps_candidates)
EOF

    return 1
}

normalize_server_root() {
    local server_root="$1"
    [ -d "$server_root" ] || fail "SE_SERVER_ROOT does not exist: $server_root"
    server_root="$(cd -P -- "$server_root" && pwd)"

    if [ "$(basename "$server_root")" = "DedicatedServer64" ]; then
        printf '%s\n' "$(cd -P -- "$server_root/.." && pwd)"
        return 0
    fi

    [ -d "$server_root/DedicatedServer64" ] || fail \
        "SE_SERVER_ROOT must point to the dedicated server root or its DedicatedServer64 directory: $server_root"
    printf '%s\n' "$server_root"
}

detect_server_root() {
    if [ -n "${SE_SERVER_ROOT:-}" ]; then
        normalize_server_root "$SE_SERVER_ROOT"
        return 0
    fi

    local steamapps
    while IFS= read -r steamapps; do
        [ -d "$steamapps" ] || continue
        local candidate="$steamapps/common/SpaceEngineersDedicatedServer"
        if [ -d "$candidate/DedicatedServer64" ]; then
            normalize_server_root "$candidate"
            return 0
        fi
    done <<EOF
$(steamapps_candidates)
EOF

    return 1
}

detect_se_appdata_dir() {
    if [ -n "${SE_APPDATA_DIR:-}" ]; then
        printf '%s\n' "$SE_APPDATA_DIR"
        return 0
    fi

    local game_root="${1:-}"
    local candidate=""
    local steamapps=""

    if [ -n "$game_root" ]; then
        steamapps="$(cd -P -- "$game_root/../.." 2>/dev/null && pwd || true)"
        if [ -n "$steamapps" ]; then
            candidate="$steamapps/compatdata/$SE_APP_ID/pfx/drive_c/users/steamuser/AppData/Roaming/SpaceEngineers"
            if [ -d "$candidate" ] || [ -d "$(dirname "$candidate")" ]; then
                printf '%s\n' "$candidate"
                return 0
            fi
        fi
    fi

    while IFS= read -r steamapps; do
        [ -d "$steamapps" ] || continue
        candidate="$steamapps/compatdata/$SE_APP_ID/pfx/drive_c/users/steamuser/AppData/Roaming/SpaceEngineers"
        if [ -d "$candidate" ] || [ -d "$(dirname "$candidate")" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done <<EOF
$(steamapps_candidates)
EOF

    return 1
}

ensure_git_repo() {
    local repo_dir="$1"
    if [ -d "$repo_dir/.git" ]; then
        return 0
    fi

    git -C "$repo_dir" init >/dev/null
    git -C "$repo_dir" symbolic-ref HEAD refs/heads/main 2>/dev/null || true
    cat >"$repo_dir/.gitignore" <<'EOF'
CodeIndex/
Content/
__pycache__/
*.py[cod]
*.bak
*.log
EOF
    git -C "$repo_dir" add .gitignore
    git -C "$repo_dir" \
        -c user.name="se-dev-skills" \
        -c user.email="se-dev-skills@localhost" \
        commit -m "Initial commit: .gitignore" >/dev/null || true
}

ensure_ilspycmd() {
    prepend_user_paths

    if [ -n "${ILSPYCMD:-}" ] && [ -x "$ILSPYCMD" ]; then
        return 0
    fi

    if command -v ilspycmd >/dev/null 2>&1; then
        ILSPYCMD="$(command -v ilspycmd)"
        export ILSPYCMD
        return 0
    fi

    require_cmd dotnet
    local tool_dir="$SE_TOOLS_ROOT/ilspycmd"
    local tool_path="$tool_dir/ilspycmd"

    if [ ! -x "$tool_path" ]; then
        mkdir -p "$tool_dir"
        log "Installing ilspycmd $ILSPY_VERSION"
        dotnet tool install --tool-path "$tool_dir" ilspycmd --version "$ILSPY_VERSION" >/dev/null
    fi

    [ -x "$tool_path" ] || fail "ilspycmd installation failed."
    ILSPYCMD="$tool_path"
    export ILSPYCMD
}
