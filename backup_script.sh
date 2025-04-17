SRC="/home/benja/Desktop/Masters/"
DEST="/media/benja/T7/"
TIMESTAMP_FILE="/media/benja/T7/last_backup_time.txt"

DATA_DEST="$DEST/masters_backup/data"
IMAGE_DEST="$DEST/masters_backup/image"

# Check that the external drive exists and is writable
if [[ ! -d "$DEST" || ! -w "$DEST" ]]; then
    echo "❌ Error: Backup drive not found or not writable at: $DEST"
    exit 1
fi

echo "✅ Backup destination found: $DEST"

# Make directories
mkdir -p "$DATA_DEST" "$IMAGE_DEST"


# Determine last backup time
if [[ -f "$TIMESTAMP_FILE" ]]; then
    LAST_BACKUP=$(cat "$TIMESTAMP_FILE")
    echo "Last backup was at: $LAST_BACKUP"
else
    echo "No previous backup found. Backing up everything."
    LAST_BACKUP="1970-01-01"
fi

echo $LAST_BACKUP

# Backup Data processing
echo "Archiving modified files in Data processing..."
for group_path in "Data Processing"/*/; do
    group_name=$(basename "$group_path")
    tar_path="$DATA_DEST/${group_name}.tar.gz"

    echo "=== $(basename "$group_path") ==="
    find "$group_path" -maxdepth 1 -type d \( -name "*.ms" -o -name "*.ms.flagversions" \) -newermt "$LAST_BACKUP" \
        -exec du -sb {} + | awk '{total += $1} END {printf "Total: %.2f GB\n", total / (1024^3)}'

    find "$group_path" -maxdepth 1 -type d \( -name "*.ms" -o -name "*.ms.flagversions" \) -newermt "$LAST_BACKUP" \
       | tar -czf "$tar_path" --files-from=- --transform="s|^|./|" --no-recursion
done

# Backup Image processing
echo "Archiving modified files in Image processing..."
for cluster_path in "Image Processing"/*/; do
    cluster_name=$(basename "$cluster_path")
    tar_path="$IMAGE_DEST/${cluster_name}.tar.gz"

    echo "=== $(basename "$cluster_path") ==="
    find "$cluster_path" -mindepth 1 -type d \( -name "*.ms" -o -name "*.ms.flagversions" \) -newermt "$LAST_BACKUP" \
        -exec du -sb {} + | awk '{total += $1} END {printf "Total: %.2f GB\n", total / (1024^3)}'

    find "$cluster_path" -mindepth 1 -type d -name \( -name "*.ms" -o -name "*.ms.flagversions" \) -newermt "$LAST_BACKUP" \
      | tar -czf "$tar_path" --files-from=- --transform="s|^|./|" --no-recursion
done

# Update timestamp
date -Iseconds > "$TIMESTAMP_FILE"
echo "Backup complete. Tarballs saved to $DEST"


