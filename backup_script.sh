SRC="/home/benc/Desktop/Masters"
BACKUP_DIR="/media/benc/T7"

DATA_DEST="$BACKUP_DIR/masters_backup/data"
IMAGE_DEST="$BACKUP_DIR/masters_backup/image"
TIMESTAMP_FILE=".last_backup"

DRY_RUN=false

# Check for dry-run argument
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 Running in dry-run mode — no files will be written."
fi

# Check that the external drive exists and is writable
if [[ ! -d "$BACKUP_DIR" || ! -w "$BACKUP_DIR" ]]; then
    echo "❌ Error: Backup drive not found or not writable at: $BACKUP_DIR"
    exit 1
fi
echo "✅ Backup destination found: $BACKUP_DIR"

# Make directories
mkdir -p "$DATA_DEST" "$IMAGE_DEST"

# Backup Data processing
for group_path in "$SRC/Data Processing"/*; do
    [ -d "$group_path" ] || continue
    group_name=$(basename "$group_path")
    echo "Processing group: $group_name"

    mkdir -p "$DATA_DEST/$group_name"

    # If no timestamp file, assume this is the first backup and create one
    TIMESTAMP_PATH="$DATA_DEST/$group_name/$TIMESTAMP_FILE"
    if [ ! -f "$TIMESTAMP_PATH" ]; then
        echo "First backup – backing up everything"
        echo 0 > "$TIMESTAMP_PATH"
    fi
    # Set the backup time
    LAST_BACKUP_TIME=$(cat "$TIMESTAMP_PATH")

    for target in "$group_path"/*.ms "$group_path"/*.ms.flagversions; do
        [ -d "$target" ] || continue
        target_name=$(basename "$target")
        dest="$DATA_DEST/$group_name"

        # Check modification time of the directory
        MOD_TIME=$(stat -c %Y "$target")

        if (( MOD_TIME > LAST_BACKUP_TIME )); then
            echo "  Copying modified $target_name -> $dest/$target_name"
            if [ "$DRY_RUN" = false ]; then
                # Copy the file and set new modified time
                echo "$MOD_TIME" > "$TIMESTAMP_PATH"
                rm -rf "$dest/$target_name"
                cp -a "$target" "$dest/$target_name"
            fi
        else
            echo "  Skipping $target (not modified)"
        fi
    done
done


echo "🖼️ Starting image backup..."

for image_group in "$SRC/Image Processing"/*; do
    [ -d "$image_group" ] || continue
    group_name=$(basename "$image_group")
    echo "📂 Processing image group: $group_name"

    for config_dir in "$image_group"/*; do
        [ -d "$config_dir" ] || continue
        config_name=$(basename "$config_dir")
        echo "  🔧 Config: $config_name"

        dest_dir="$IMAGE_DEST/$group_name/$config_name"
        mkdir -p "$dest_dir"

        # Most recent -pX.image.tt0
        latest_image_file=$(find "$config_dir" -type d -name "*-p*.image.tt0" -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2-)

        # Earliest .ms file that is not a -pX.ms
        earliest_ms_file=$(find "$config_dir" -type d -name "*.ms" ! -name "*-p*.ms" -printf "%T@ %p\n" | sort -n | head -1 | cut -d' ' -f2-)

        for file in "$earliest_ms_file" "$latest_image_file"; do
            [ -e "$file" ] || continue
            filename=$(basename "$file")
            dest="$dest_dir/$filename"

            if [ "$DRY_RUN" = true ]; then
                echo "    Would copy $file -> $dest"
            else
                echo "    Copying $file -> $dest"
                cp -a "$file" "$dest"
            fi
        done
    done
done


# Finish up
if [ "$DRY_RUN" = false ]; then
    echo "✅ Incremental backup complete."
else
    echo "ℹ️ Dry-run complete — no files changed, timestamp not updated."
fi
