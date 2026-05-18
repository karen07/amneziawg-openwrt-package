#!/bin/sh

SCRIPT_DIR=$(CDPATH='' cd "$(dirname "$0")" && pwd) || exit 1
CALLER_DIR=$(pwd)
CONFIG_FILE="$SCRIPT_DIR/openwrt-build.env"
WORK_DIR="$SCRIPT_DIR/.openwrt-build"

[ -f "$CONFIG_FILE" ] || {
    echo "Missing config: $CONFIG_FILE" >&2
    exit 1
}

# shellcheck disable=SC1090
. "$CONFIG_FILE"

: "${PACKAGE_DIRS:=}"
: "${PACKAGE_OUTPUTS:=}"

green=$(printf '\033[0;32m')
red=$(printf '\033[0;31m')
reset=$(printf '\033[0m')

die() {
    printf '%s%s%s\n' "$red" "$*" "$reset" >&2
    exit 1
}

need_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "Missing command: $1"
}

package_name_from_dir() {
    package_dir=$(basename "$1")

    case "$package_dir" in
        *-openwrt-package)
            printf '%s\n' "${package_dir%-openwrt-package}"
            ;;
        *)
            printf '%s\n' "$package_dir"
            ;;
    esac
}

sdk_package_dir_name() {
    package_name=$(package_name_from_dir "$1")

    printf '%s-openwrt-package\n' "$package_name"
}

mapped_output_package_name() {
    package_dir="$1"
    package_name=$(package_name_from_dir "$package_dir")

    printf '%s\n' "$PACKAGE_OUTPUTS" \
        | while IFS='=' read -r source_name output_name; do
            [ -n "$source_name" ] || continue
            [ "$source_name" = "$package_name" ] || continue
            [ -n "$output_name" ] || continue

            printf '%s\n' "$output_name"
            break
        done
}

output_package_name() {
    package_dir="$1"
    package_name=$(package_name_from_dir "$package_dir")
    mapped_name=$(mapped_output_package_name "$package_dir")

    if [ -n "$mapped_name" ]; then
        printf '%s\n' "$mapped_name"
    else
        printf '%s\n' "$package_name"
    fi
}

package_dir_for_name() {
    wanted="$1"

    for package_dir in $PACKAGE_DIRS; do
        package_name=$(package_name_from_dir "$package_dir")
        output_name=$(output_package_name "$package_dir")

        if [ "$package_name" = "$wanted" ] || [ "$output_name" = "$wanted" ]; then
            printf '%s\n' "$package_dir"
            return 0
        fi
    done

    return 1
}

package_names() {
    for package_dir in $PACKAGE_DIRS; do
        output_package_name "$package_dir"
    done
}

usage() {
    cat <<'EOF_USAGE'
Usage:
  ./openwrt-build.sh install <package> <router>
  ./openwrt-build.sh build-router <package> <router> <version> [output-dir]
  ./openwrt-build.sh build-target <package> <version> <target> <subtarget> <pkgarch> [output-dir]

Modes:
  install       Detect version/target/arch from router, build package, install to router.
  build-router  Detect target/arch from router, use explicit version, save package locally.
  build-target  Use explicit version/target/subtarget/pkgarch, save package locally.

Packages:
EOF_USAGE

    package_names | sed 's/^/  /'
    echo "  all"

    cat <<'EOF_USAGE'

Examples:
  ./openwrt-build.sh install all router
  ./openwrt-build.sh build-router all router 25.12.5
  ./openwrt-build.sh build-router all router 25.12.5 release
  ./openwrt-build.sh build-target all 25.12.5 x86 64 x86_64 release
EOF_USAGE
}

[ -n "$PACKAGE_DIRS" ] || die "PACKAGE_DIRS is empty in $CONFIG_FILE"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
    exit 0
fi

for package_dir in $PACKAGE_DIRS; do
    [ -d "$SCRIPT_DIR/$package_dir" ] \
        || die "Missing package directory: $SCRIPT_DIR/$package_dir"
done

MODE="${1:-}"

PACKAGE_NAME=""
ROUTER=""
VERSION=""
TARGET=""
SUBTARGET=""
BOARD=""
BOARD_ARCH=""
OUTPUT_DIR=""
COPY_ONLY=""

case "$MODE" in
    install)
        [ "$#" -eq 3 ] || {
            usage
            exit 1
        }

        PACKAGE_NAME="$2"
        ROUTER="$3"
        ;;

    build-router)
        [ "$#" -eq 4 ] || [ "$#" -eq 5 ] || {
            usage
            exit 1
        }

        PACKAGE_NAME="$2"
        ROUTER="$3"
        VERSION="$4"
        OUTPUT_DIR="${5:-}"
        COPY_ONLY=1
        ;;

    build-target)
        [ "$#" -eq 6 ] || [ "$#" -eq 7 ] || {
            usage
            exit 1
        }

        PACKAGE_NAME="$2"
        VERSION="$3"
        TARGET="$4"
        SUBTARGET="$5"
        BOARD="$TARGET/$SUBTARGET"
        BOARD_ARCH="$6"
        OUTPUT_DIR="${7:-}"
        COPY_ONLY=1
        ;;

    *)
        usage
        exit 1
        ;;
esac

if [ "$PACKAGE_NAME" = "all" ]; then
    SELECTED_PACKAGE_DIRS="$PACKAGE_DIRS"
else
    selected_package_dir=$(package_dir_for_name "$PACKAGE_NAME") \
        || die "Invalid package name: $PACKAGE_NAME"
    SELECTED_PACKAGE_DIRS="$selected_package_dir"
fi

for cmd in \
    awk basename cp curl find git head make mkdir mv nproc pwd \
    rm sed tar wc; do
    need_cmd "$cmd"
done

if [ -n "$ROUTER" ]; then
    need_cmd ssh

    OS_RELEASE="$(
        ssh -o StrictHostKeyChecking=no "$ROUTER" cat /etc/os-release
    )" || die "Cannot read /etc/os-release from router: $ROUTER"
fi

os_release_value() {
    key="$1"

    printf '%s\n' "$OS_RELEASE" | awk -F= -v key="$key" '
        $1 == key {
            value = $0
            sub(/^[^=]*=/, "", value)
            gsub(/^"|"$/, "", value)
            print value
            exit
        }
    '
}

if [ -n "$ROUTER" ]; then
    [ -n "$VERSION" ] || VERSION="$(os_release_value VERSION)"

    BOARD="$(os_release_value OPENWRT_BOARD)"
    BOARD_ARCH="$(os_release_value OPENWRT_ARCH)"

    TARGET="${BOARD%%/*}"
    SUBTARGET="${BOARD#*/}"
fi

[ -n "$VERSION" ] || die "Cannot determine OpenWrt VERSION"
[ -n "$BOARD" ] || die "Cannot determine OPENWRT_BOARD"
[ -n "$BOARD_ARCH" ] || die "Cannot determine OPENWRT_ARCH"
[ -n "$TARGET" ] || die "Cannot determine OpenWrt target from OPENWRT_BOARD"
[ -n "$SUBTARGET" ] || die "Cannot determine OpenWrt subtarget from OPENWRT_BOARD"

if [ -z "$COPY_ONLY" ]; then
    need_cmd scp
fi

if [ -n "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR" || die "Cannot create output dir: $OUTPUT_DIR"
    OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)" || die "Cannot resolve output dir: $OUTPUT_DIR"
fi

mkdir -p "$WORK_DIR" || die "Cannot create work dir: $WORK_DIR"
cd "$WORK_DIR" || die "Cannot enter work dir: $WORK_DIR"

SDK_URL="https://downloads.openwrt.org/releases/$VERSION/targets/$BOARD/"

echo "MODE:          $MODE"
echo "PACKAGE:       $PACKAGE_NAME"
echo "PACKAGE_DIRS:  $SELECTED_PACKAGE_DIRS"
echo "ROUTER:        ${ROUTER:-<none>}"
echo "VERSION:       $VERSION"
echo "BOARD:         $BOARD"
echo "TARGET:        $TARGET"
echo "SUBTARGET:     $SUBTARGET"
echo "BOARD_ARCH:    $BOARD_ARCH"
echo "SDK_URL:       $SDK_URL"
echo

SDK_HTML="$(curl -fsSL "$SDK_URL")" || die "Cannot read SDK directory: $SDK_URL"

SDK_ARCHIVE=$(
    printf '%s\n' "$SDK_HTML" \
        | sed -n 's/.*href="\([^"]*openwrt-sdk[^"]*\.tar\.\(xz\|zst\|gz\)\)".*/\1/p' \
        | head -n 1
)

[ -n "$SDK_ARCHIVE" ] || die "Cannot find SDK archive"

case "$SDK_ARCHIVE" in
    *.tar.zst)
        need_cmd zstd
        SDK_DIR="${SDK_ARCHIVE%.tar.zst}"
        ;;
    *.tar.xz)
        need_cmd xz
        SDK_DIR="${SDK_ARCHIVE%.tar.xz}"
        ;;
    *.tar.gz)
        need_cmd gzip
        SDK_DIR="${SDK_ARCHIVE%.tar.gz}"
        ;;
    *)
        die "Unsupported SDK archive format: $SDK_ARCHIVE"
        ;;
esac

if [ ! -f "$SDK_ARCHIVE" ]; then
    echo "Downloading $SDK_ARCHIVE"

    tmp_archive="$SDK_ARCHIVE.tmp"
    rm -f "$tmp_archive"

    curl -fL -o "$tmp_archive" "$SDK_URL$SDK_ARCHIVE" \
        || {
            rm -f "$tmp_archive"
            die "Cannot download SDK archive: $SDK_ARCHIVE"
        }

    mv "$tmp_archive" "$SDK_ARCHIVE" \
        || {
            rm -f "$tmp_archive"
            die "Cannot save SDK archive: $SDK_ARCHIVE"
        }
fi

if [ ! -d "$SDK_DIR" ]; then
    echo "Extracting $SDK_ARCHIVE"

    tar -xf "$SDK_ARCHIVE" \
        || {
            rm -rf "$SDK_DIR"
            rm -f "$SDK_ARCHIVE"
            die "Cannot extract SDK archive: $SDK_ARCHIVE"
        }
fi

cd "$SDK_DIR" || die "Cannot enter SDK dir: $SDK_DIR"

if [ -f feeds.conf.default ]; then
    sed -i -E \
        's#https://git\.openwrt\.org/[^/]+/#https://github.com/openwrt/#g' \
        feeds.conf.default || die "Cannot rewrite feeds.conf.default"
fi

echo "Updating feeds"
./scripts/feeds update -a || die "feeds update failed"

echo "Installing feeds"
./scripts/feeds install -a || die "feeds install failed"

prepare_package_dir() {
    package_dir="$1"
    sdk_package_dir=$(sdk_package_dir_name "$package_dir")
    src="$SCRIPT_DIR/$package_dir"
    dst="package/$sdk_package_dir"

    echo "Copying $package_dir -> $dst"

    rm -rf "$dst" || die "Cannot remove $dst"
    mkdir -p "$dst" || die "Cannot create $dst"
    cp -a "$src/." "$dst/" || die "Cannot copy $package_dir"
}

# Copy all configured package definitions so dependencies between packages in
# the same repository are available even when only one package is selected.
for package_dir in $PACKAGE_DIRS; do
    prepare_package_dir "$package_dir"
done

make defconfig || die "defconfig failed"

find_apk() {
    package_name="$1"

    find bin -type f -name "${package_name}-*.apk"
}

remove_old_apks() {
    package_name="$1"

    find bin -type f -name "${package_name}-*.apk" \
        -delete 2>/dev/null || true
}

release_apk_name() {
    package_name="$1"

    printf '%s_v%s_%s_%s_%s.apk\n' \
        "$package_name" \
        "$VERSION" \
        "$BOARD_ARCH" \
        "$TARGET" \
        "$SUBTARGET"
}

install_or_copy_apk() {
    package_name="$1"
    apk_path="$2"
    apk_file=$(basename "$apk_path")

    if [ -n "$COPY_ONLY" ]; then
        release_name=$(release_apk_name "$package_name")

        if [ -n "$OUTPUT_DIR" ]; then
            destination="$OUTPUT_DIR/$release_name"
        else
            destination="$CALLER_DIR/$release_name"
        fi

        cp "$apk_path" "$destination" \
            || die "Cannot save $release_name"

        echo "Saved: $destination"
        return
    fi

    remote_apk="/tmp/$apk_file"

    scp -O "$apk_path" "$ROUTER:$remote_apk" \
        || die "Cannot copy $apk_file to router"

    # shellcheck disable=SC2029
    ssh "$ROUTER" "apk del '$package_name' || true" \
        || die "Cannot remove old package on router: $package_name"

    # shellcheck disable=SC2029
    ssh "$ROUTER" "apk add --allow-untrusted '$remote_apk'" \
        || die "Cannot install package on router: $apk_file"

    # shellcheck disable=SC2029
    ssh "$ROUTER" "rm -f '$remote_apk'" \
        || die "Cannot remove temporary package from router: $apk_file"
}

if [ -z "$COPY_ONLY" ]; then
    ssh "$ROUTER" apk update \
        || die "apk update failed on router"
fi

for package_dir in $SELECTED_PACKAGE_DIRS; do
    sdk_package_dir=$(sdk_package_dir_name "$package_dir")
    path="package/$sdk_package_dir"
    output_package=$(output_package_name "$package_dir")

    echo
    echo "Building $sdk_package_dir"
    echo

    remove_old_apks "$output_package"

    if ! make "$path/clean"; then
        make -j1 V=s "$path/clean" || true
        die "Clean failed: $package_dir"
    fi

    if ! make -j"$(nproc)" "$path/compile"; then
        make -j1 V=s "$path/compile" || true
        die "Build failed: $package_dir"
    fi

    apk_path=$(find_apk "$output_package")

    [ -n "$apk_path" ] || die "APK not found for $output_package"

    apk_count=$(printf '%s\n' "$apk_path" | wc -l)

    [ "$apk_count" -eq 1 ] \
        || die "Expected one APK for $output_package, found $apk_count"

    [ -f "$apk_path" ] || die "APK not found for $output_package: $apk_path"

    install_or_copy_apk "$output_package" "$apk_path"

    printf '%sOK: %s%s\n' "$green" "$output_package" "$reset"
done

printf '%sAll done: %s%s\n' "$green" "$PACKAGE_NAME" "$reset"
