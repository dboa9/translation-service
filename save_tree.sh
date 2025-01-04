#!/bin/bash

# File: generate_tree_report.sh
# Location: /path/to/your/scripts/directory/generate_tree_report.sh

# Debugging
set -x

# Get the current date and time in the desired format
timestamp=$(date '+_%d_%m_%y_%H_%M')
timestamp_display=$(date '+%Y-%m-%d %H:%M:%S') # Separate format for display

# Define the directory path for tree output
DIRECTORY_PATH="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project"

# Prompt for the base filename
read -p "Enter the base filename (without extension): " basename

# Prompt for a custom directory to save the file
read -p "Enter the directory to save the file (leave blank for current directory): " directory
directory=${directory:-"."} # Default to the current directory if none provided

# Path for checking any files with the same base name
basepath="${directory%/}/${basename}"

# Function to generate file content
generate_file_content() {
    echo "Generating content for $1..."
    # Generate tree output with refined exclusions
    tree --dirsfirst -d -I '__pycache__|*.pyc|*.bak|*.lock|node_modules|redundant_backup|versions|examples' \
        "$DIRECTORY_PATH" | \
        sed -E '/^\.\/backup_before_rename|backups|dataset_cache|datasets_cache|logs|old_scripts_backup|redundant_backup/d' \
        >"$1"

    echo "Generated on: $timestamp_display" >>"$1"
    echo "File created at $1"
}

# Function to remove existing files with the same base name (ignoring timestamp)
remove_existing_files() {
    echo "Checking for files with the base name '$basename' to remove..."
    files_to_remove=$(ls "${basepath}"_*.txt 2>/dev/null)
    if [[ -n "$files_to_remove" ]]; then
        echo "Removing existing files with the same base name:"
        echo "$files_to_remove"
        rm -f $files_to_remove
    fi
}

# Check if any file with the base name exists (with or without timestamp)
existing_files=$(ls "$basepath"*.txt 2>/dev/null)

if [[ -n "$existing_files" ]]; then
    echo "A file with the name starting with '$basename' already exists in $directory."
    echo "Please select an option:"
    echo "1) Overwrite the existing file (remove all existing files with the same base name)"
    echo "2) Append to the existing file"
    echo "3) Save as a new file with timestamp"
    echo "4) Enter a new filename"
    echo "5) Exit without making changes"
    read -p "Enter your choice (1/2/3/4/5): " choice

    case $choice in
    1)
        # Overwrite the existing file by removing all matching files first
        remove_existing_files
        filepath="${basepath}${timestamp}.txt"
        generate_file_content "$filepath"
        echo "File overwritten and saved as $filepath."
        ;;
    2)
        # Append to the existing file without adding a timestamp
        filepath="${basepath}.txt"
        tree --dirsfirst -d -I '__pycache__|*.pyc|*.bak|*.lock|node_modules|redundant_backup|versions|examples' \
            "$DIRECTORY_PATH" | \
            sed -E '/^\.\/backup_before_rename|backups|dataset_cache|datasets_cache|logs|old_scripts_backup|redundant_backup/d' \
            >>"$filepath"
        echo "Appended new data on $timestamp_display." >>"$filepath"
        echo "Data appended to existing file at $filepath."
        ;;
    3)
        # Save as a new file with timestamp
        filepath="${basepath}${timestamp}.txt"
        generate_file_content "$filepath"
        echo "File saved as $filepath"
        ;;
    4)
        # Prompt for a new filename and save with timestamp
        read -p "Enter a new base filename (without extension): " new_basename
        filepath="${directory%/}/${new_basename}${timestamp}.txt"
        generate_file_content "$filepath"
        echo "File saved as $filepath"
        ;;
    5)
        echo "No changes made."
        exit 0
        ;;
    *)
        echo "Invalid choice. No changes made."
        exit 1
        ;;
    esac
else
    # No matching files found, create a new file with timestamp
    filepath="${basepath}${timestamp}.txt"
    generate_file_content "$filepath"
    echo "New file created as $filepath"
fi

# Optional: Prompt to open file in text editor
read -p "Would you like to open the file in a text editor? (y/n): " open_choice
if [[ "$open_choice" =~ ^[Yy]$ ]]; then
    nano "$filepath" # Replace with preferred editor
fi