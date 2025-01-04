# deployment/scripts/update_paths.sh.sh
#!/bin/bash
source config/file_mappings.sh

# Update symlinks to point to latest versions
ln -sf "${FILE_MAPPINGS["web_interface"]["location"]}"/"${FILE_MAPPINGS["web_interface"]["current"]}" \
    "${BASE_DIR}"/core/interfaces/web_interface.py