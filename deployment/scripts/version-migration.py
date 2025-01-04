# File: version-migration.py
"""
Note: This code should be saved with the current GMT date and time in the format:
migrate_versions.py
Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project/deployment/scripts/migrate_versions.py
Author: dboa9 (danielalchemy9@gmail.com)
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Define COMPONENT_MAPPINGS directly in this script
COMPONENT_MAPPINGS = {
    "interfaces": "web_interface",
    "dataset": "dataset_loader",
    "monitoring": "monitoring",
    "deployment": "deployment",
    "other": "other"
}

try:
    from core.utils.version_manager import VersionManager
except ImportError:
    logging.error("Failed to import VersionManager. Make sure the core module is in the Python path.")
    raise

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='version_migration.log'
)
logger = logging.getLogger(__name__)

class VersionMigrator:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project")
        self.old_versions_dir = self.base_dir / "versions"
        self.old_version_file = self.old_versions_dir / "version_history.json"
        self.backup_dir = self.base_dir / "versions" / "backup" / "pre_migration"
        self.version_manager = VersionManager()

    def backup_old_versions(self):
        """Backup old version data before migration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)

        if self.old_version_file.exists():
            shutil.copy2(self.old_version_file, backup_path / "version_history.json")
            logger.info(f"Backed up old version history to {backup_path}")

        # Backup old version files
        if self.old_versions_dir.exists():
            for file in self.old_versions_dir.glob("*"):
                if file.is_file() and file.name != "version_history.json":
                    shutil.copy2(file, backup_path / file.name)
            logger.info("Backed up old version files")

    def load_old_versions(self) -> Dict:
        """Load old version history"""
        if not self.old_version_file.exists():
            logger.warning("No old version history found")
            return {}

        try:
            with open(self.old_version_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON in old version history: {e}")
        except Exception as e:
            logger.error(f"Error loading old version history: {e}")
        return {}

    def map_old_to_new(self, old_data: Dict) -> Dict[str, List[Dict]]:
        """Map old version data to new structure"""
        new_data = {}
        
        # Component type mapping
        type_mapping = {v: k for k, v in COMPONENT_MAPPINGS.items()}

        for component, versions in old_data.items():
            comp_type = type_mapping.get(component, "other")
            if comp_type not in new_data:
                new_data[comp_type] = []

            # Convert version data
            for version in versions:
                new_version = {
                    "version": version.get("version", "unknown"),
                    "timestamp": version.get("timestamp", ""),
                    "changes": version.get("changes", ""),
                    "backup_path": version.get("backup_path", "")
                }
                new_data[comp_type].append(new_version)

        return new_data

    def migrate_versions(self):
        """Migrate old version data to new system"""
        logger.info("Starting version migration...")

        # Backup existing data
        self.backup_old_versions()

        # Load old version data
        old_data = self.load_old_versions()
        if not old_data:
            logger.warning("No old version data to migrate")
            return

        # Map to new structure
        new_data = self.map_old_to_new(old_data)

        # Import into new system
        for comp_type, versions in new_data.items():
            for version in versions:
                try:
                    self.version_manager.update_component(
                        comp_type,
                        version["version"],
                        version["version"],
                        version["changes"]
                    )
                except Exception as e:
                    logger.error(
                        f"Error migrating version {version['version']} for component {comp_type}: {e}"
                    )

        logger.info("Version migration completed")

    def verify_migration(self) -> bool:
        """Verify migration success"""
        # Check if all components were migrated
        old_data = self.load_old_versions()
        if not old_data:
            logger.info("No old data to verify against")
            return True

        success = True
        for comp_type in COMPONENT_MAPPINGS:
            try:
                history = self.version_manager.get_component_history(comp_type, "current")
                if not history:
                    logger.error(f"No history found for component type: {comp_type}")
                    success = False
                else:
                    logger.info(f"Successfully migrated {comp_type} with {len(history)} versions")
            except Exception as e:
                logger.error(f"Error verifying migration for component {comp_type}: {e}")
                success = False

        return success

def main():
    try:
        migrator = VersionMigrator()
        migrator.migrate_versions()
        if migrator.verify_migration():
            logger.info("Migration completed successfully")
        else:
            logger.error("Migration verification failed")
    except Exception as e:
        logger.exception(f"An unexpected error occurred during migration: {e}")

if __name__ == "__main__":
    main()
