# File: consolidation-guide_1_11_24_21_27.py
"""
Note: This code should be saved with the current GMT date and time in the format:
consolidation_guide.py
Location: /home/ubuntu/darija_project_new/deployment/scripts/consolidation_guide.py
Author: dboa9 (danielalchemy9@gmail.com)
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from core.utils.path_management import PathManager
from core.utils.consolidation_rollback import ConsolidationRollback

# Additional path mappings
ENVIRONMENT_PATHS = {
    "ec2": {
        "base": Path("/home/ubuntu/darija_project_new"),
        "data": Path("/home/ubuntu/datasets_cache"),
        "models": Path("/home/ubuntu/darija_project_new/models/checkpoints")
    },
    "windows": {
        "base": Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project"),
        "data": Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/datasets"),
        "models": Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/models")
    },
    "ubuntu": {
        "base": Path("/home/mrdbo/darija_project"),
        "data": Path("/home/mrdbo/datasets"),
        "models": Path("/home/mrdbo/models")
    }
}

class ConsolidationGuide:
    def __init__(self):
        self.path_manager = PathManager()
        self.rollback = ConsolidationRollback()
        self.logger = logging.getLogger("ConsolidationGuide")
        
    def consolidate_component(self, component_type: str, component_name: str) -> bool:
        """Consolidate a specific component"""
        try:
            # Create snapshot first
            snapshot = self.rollback.create_snapshot(
                f"Pre-consolidation of {component_type}/{component_name}"
            )
            if not snapshot:
                return False
                
            # Backup component
            backup_path = self.path_manager.backup_component(
                component_type, 
                component_name
            )
            if not backup_path:
                return False
                
            # Migrate imports
            success = self.path_manager.migrate_imports(
                Path(component_name)
            )
            
            if success:
                self.logger.info(
                    f"Successfully consolidated {component_type}/{component_name}"
                )
                return True
            else:
                # Rollback if migration failed
                self.rollback.rollback_to_snapshot(snapshot)
                return False
                
        except Exception as e:
            self.logger.error(
                f"Error consolidating {component_type}/{component_name}: {str(e)}"
            )
            return False
            
    def verify_environment_paths(self, env: str) -> Dict[str, bool]:
        """Verify paths for a specific environment"""
        if env not in ENVIRONMENT_PATHS:
            return {}
            
        results = {}
        for path_type, path in ENVIRONMENT_PATHS[env].items():
            results[path_type] = path.exists()
            
        return results
        
    def sync_environments(self, source: str, target: str) -> bool:
        """Sync between environments"""
        if source not in ENVIRONMENT_PATHS or target not in ENVIRONMENT_PATHS:
            return False
            
        try:
            import shutil
            
            source_paths = ENVIRONMENT_PATHS[source]
            target_paths = ENVIRONMENT_PATHS[target]
            
            # Sync each directory
            for path_type in ["base", "data", "models"]:
                src = source_paths[path_type]
                dst = target_paths[path_type]
                
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing environments: {str(e)}")
            return False

# Usage examples
def consolidation_examples():
    guide = ConsolidationGuide()
    
    print("\nExample 1: Consolidate Monitoring Dashboard")
    print("-------------------------------------------")
    if guide.consolidate_component("monitoring", "monitoring-dashboard-structure.ts"):
        print("✓ Successfully consolidated dashboard component")
    else:
        print("✗ Failed to consolidate dashboard component")
        
    print("\nExample 2: Verify Environment Paths")
    print("-----------------------------------")
    for env in ENVIRONMENT_PATHS:
        results = guide.verify_environment_paths(env)
        print(f"\n{env} environment:")
        for path_type, exists in results.items():
            print(f"  {'✓' if exists else '✗'} {path_type}")
            
    print("\nExample 3: Sync Environments")
    print("----------------------------")
    if guide.sync_environments("ec2", "ubuntu"):
        print("✓ Successfully synced EC2 to Ubuntu")
    else:
        print("✗ Failed to sync environments")

def main():
    print("Component Consolidation Guide")
    print("============================")
    
    # Get user input for operation
    print("\nAvailable operations:")
    print("1. Consolidate specific component")
    print("2. Verify environment paths")
    print("3. Sync environments")
    print("4. Run examples")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ")
    
    guide = ConsolidationGuide()
    
    if choice == "1":
        component_type = input("Enter component type: ")
        component_name = input("Enter component name: ")
        guide.consolidate_component(component_type, component_name)
    elif choice == "2":
        env = input("Enter environment (ec2/windows/ubuntu): ")
        results = guide.verify_environment_paths(env)
        for path_type, exists in results.items():
            print(f"{path_type}: {'✓' if exists else '✗'}")
    elif choice == "3":
        source = input("Enter source environment: ")
        target = input("Enter target environment: ")
        guide.sync_environments(source, target)
    elif choice == "4":
        consolidation_examples()
    
if __name__ == "__main__":
    main()
