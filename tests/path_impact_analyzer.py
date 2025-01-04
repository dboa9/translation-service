"""
Path Impact Analyzer
Created: 2024-11-12 11:00 GMT
Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/translation_service/tests/path_impact_analyzer.py
Author: dboa9 (danielalchemy9@gmail.com)
"""

import ast
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class AnalysisResult:
    file_path: str
    imports: List[str]
    references: List[str]
    dependencies: List[str]

class ImpactAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.setup_logging()
        
        self.redundant_files: Set[str] = set()
        self.affected_imports: Dict[str, List[str]] = {}
        self.affected_references: Dict[str, List[str]] = {}
        self.file_cache: Dict[str, AnalysisResult] = {}
        
    def setup_logging(self):
        """Configure logging with file and console handlers"""
        self.logger = logging.getLogger("ImpactAnalyzer")
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"impact_analysis_{timestamp}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)

    def find_redundant_files(self) -> Set[str]:
        """
        Identify files that are not referenced by any other files in the project
        Returns: Set of file paths that are potentially redundant
        """
        all_files = set(f.relative_to(self.project_root).as_posix()
                       for f in self.project_root.rglob("*.py")
                       if not any(part.startswith('.') for part in f.parts))
        
        referenced_files = set()
        for file_path in all_files:
            try:
                analysis = self._analyze_file(Path(file_path))
                referenced_files.update(analysis.dependencies)
            except Exception as e:
                self.logger.warning(f"Error analyzing {file_path}: {e}")
        
        self.redundant_files = all_files - referenced_files
        return self.redundant_files

    def analyze_imports(self) -> Dict[str, List[str]]:
        """
        Analyze all import statements in the project
        Returns: Dictionary mapping files to their import statements
        """
        for file_path in self.project_root.rglob("*.py"):
            if any(part.startswith('.') for part in file_path.parts):
                continue
                
            try:
                relative_path = file_path.relative_to(self.project_root).as_posix()
                analysis = self._analyze_file(file_path)
                self.affected_imports[relative_path] = analysis.imports
            except Exception as e:
                self.logger.warning(f"Error analyzing imports in {file_path}: {e}")
        
        return self.affected_imports

    def analyze_references(self) -> Dict[str, List[str]]:
        """
        Analyze all file references in the project
        Returns: Dictionary mapping files to their references
        """
        for file_path in self.project_root.rglob("*.py"):
            if any(part.startswith('.') for part in file_path.parts):
                continue
                
            try:
                relative_path = file_path.relative_to(self.project_root).as_posix()
                analysis = self._analyze_file(file_path)
                self.affected_references[relative_path] = analysis.references
            except Exception as e:
                self.logger.warning(f"Error analyzing references in {file_path}: {e}")
        
        return self.affected_references

    def analyze_path_change(self, old_path: str, new_path: str) -> Dict[str, List[str]]:
        """
        Analyze the impact of moving a file from old_path to new_path
        Returns: Dictionary of affected files and their references that need updating
        """
        affected_files = {}
        
        # Analyze imports and references
        self.analyze_imports()
        self.analyze_references()
        
        # Find files affected by the path change
        for file_path, imports in self.affected_imports.items():
            if old_path in imports:
                affected_files[file_path] = ['import']
                
        for file_path, refs in self.affected_references.items():
            if old_path in refs:
                if file_path in affected_files:
                    affected_files[file_path].append('reference')
                else:
                    affected_files[file_path] = ['reference']
        
        return affected_files

    def generate_report(self) -> Dict:
        """Generate a comprehensive analysis report"""
        self.find_redundant_files()
        self.analyze_imports()
        self.analyze_references()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'redundant_files': list(self.redundant_files),
            'affected_files': {
                file: {
                    'imports': self.affected_imports.get(file, []),
                    'references': self.affected_references.get(file, [])
                }
                for file in set(self.affected_imports.keys()) | set(self.affected_references.keys())
            }
        }
        
        return report

    def save_report(self, report: Dict, filename: Optional[str] = None) -> Path:
        """Save the analysis report to a JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"impact_analysis_{timestamp}.json"
            
        report_path = self.project_root / "reports" / filename
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"Report saved to {report_path}")
        return report_path

    def _analyze_file(self, file_path: Path) -> AnalysisResult:
        """
        Analyze a single file for imports and references
        Returns: AnalysisResult containing imports and references
        """
        if str(file_path) in self.file_cache:
            return self.file_cache[str(file_path)]
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            tree = ast.parse(content)
            imports = []
            references = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                elif isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Load):
                        references.append(node.id)
                        
            result = AnalysisResult(
                file_path=str(file_path),
                imports=imports,
                references=references,
                dependencies=list(set(imports + references))
            )
            
            self.file_cache[str(file_path)] = result
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    project_root = Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project")
    analyzer = ImpactAnalyzer(project_root)
    
    print("\nGenerating impact analysis report...")
    report = analyzer.generate_report()
    analyzer.save_report(report)
    
    print("\nRedundant Files:")
    for file in report["redundant_files"]:
        print(f"  - {file}")
        
    print("\nAffected Files:")
    for file, info in report["affected_files"].items():
        print(f"\n  File: {file}")
        if info['imports']:
            print(f"    Imports: {', '.join(info['imports'])}")
        if info['references']:
            print(f"    References: {', '.join(info['references'])}")
        
    print("\nDetailed report saved to reports/impact_analysis.json")
