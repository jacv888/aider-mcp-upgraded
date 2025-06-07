import os
import logging
import time
from pathlib import Path
from typing import List, Dict, Set, Any, Optional, Tuple, Union
from collections import defaultdict

# Assuming get_logger is available from app.core.logging
try:
    from app.core.logging import get_logger
    from app.core.config import get_config
except ImportError:
    # Fallback for standalone testing or if logging/config modules are not yet integrated
    logging.basicConfig(level=logging.INFO)
    def get_logger(name, log_category="operational"):
        return logging.getLogger(name)
    # Dummy Config class for standalone testing
    class DummyFeaturesConfig:
        enable_conflict_detection = True
        conflict_detection_timeout = 5
        enable_conflict_logging = True
        conflict_report_verbosity = "standard"
    class DummyConfig:
        features = DummyFeaturesConfig()
    def get_config():
        return DummyConfig()


logger = get_logger(__name__, "operational")

class FileConflictDetector:
    """
    Detects overlapping editable files across multiple parallel tasks.

    This class provides functionality to:
    - Normalize file paths (handling relative/absolute paths and symlinks).
    - Identify which tasks have common editable files.
    - Generate clear reports detailing detected conflicts.
    - Configure behavior via the application's Config class (specifically, config.features):
      - enable_conflict_detection (bool): Enable or disable conflict detection (default: True).
      - conflict_detection_timeout (int): Timeout in seconds for conflict detection (default: 5).
      - enable_conflict_logging (bool): Enable or disable logging of conflicts (default: True).
      - conflict_report_verbosity (str): Verbosity level for conflict reports: minimal, standard, verbose (default: standard).

    It is designed to be robust, handling edge cases like empty lists or invalid paths,
    and includes proper logging and error handling for production readiness.
    """

    def __init__(self, working_dir: Optional[str] = None):
        """
        Initializes the FileConflictDetector.

        Args:
            working_dir (Optional[str]): The base directory against which relative
                                         paths will be resolved. If None, the current
                                         working directory will be used.
        """
        self.working_dir = Path(working_dir).resolve() if working_dir else Path.cwd().resolve()

        try:
            self.config = get_config()
            features_config = self.config.features
        except Exception as e:
            logger.error(f"Failed to load configuration for conflict detector, using defaults: {e}")
            # Fallback to a dummy object that will return defaults via getattr
            class FallbackFeaturesConfig:
                pass
            features_config = FallbackFeaturesConfig()

        self.enable_conflict_detection = getattr(features_config, "enable_conflict_detection", True)
        self.conflict_detection_timeout = getattr(features_config, "conflict_detection_timeout", 5)
        self.enable_conflict_logging = getattr(features_config, "enable_conflict_logging", True)
        
        # For verbosity, ensure it's a string and lowercased, then validate
        verbosity_from_config = getattr(features_config, "conflict_report_verbosity", "standard")
        self.conflict_report_verbosity = str(verbosity_from_config).lower()
        if self.conflict_report_verbosity not in {"minimal", "standard", "verbose"}:
            self.conflict_report_verbosity = "standard"

        if self.enable_conflict_logging:
            logger.info(f"FileConflictDetector initialized with working directory: {self.working_dir}")
            logger.info(f"Conflict detection enabled (from config): {self.enable_conflict_detection}")
            logger.info(f"Conflict detection timeout (from config): {self.conflict_detection_timeout} seconds")
            logger.info(f"Conflict logging enabled (from config): {self.enable_conflict_logging}")
            logger.info(f"Conflict report verbosity (from config): {self.conflict_report_verbosity}")

    def is_conflict_detection_enabled(self) -> bool:
        """
        Checks if conflict detection is enabled via configuration.

        Returns:
            bool: True if enabled, False otherwise.
        """
        return self.enable_conflict_detection

    def _normalize_path(self, file_path: str) -> Optional[str]:
        """
        Normalizes a single file path to its absolute, canonical form.

        Handles relative paths by resolving them against the working_dir and
        resolves any symlinks.

        Args:
            file_path (str): The path to normalize.

        Returns:
            Optional[str]: The normalized absolute path as a string, or None if
                           the path cannot be resolved or is invalid.
        """
        if not file_path:
            if self.enable_conflict_logging:
                logger.warning("Attempted to normalize an empty or None file path.")
            return None
        try:
            # Convert to Path object
            p = Path(file_path)

            # If relative, resolve against working_dir
            if not p.is_absolute():
                p = self.working_dir / p

            # Resolve symlinks and get the canonical path
            normalized_p = p.resolve()
            return str(normalized_p)
        except Exception as e:
            if self.enable_conflict_logging:
                logger.error(f"Failed to normalize path '{file_path}': {e}")
            return None

    def _normalize_paths_list(self, file_paths: List[str]) -> Set[str]:
        """
        Normalizes a list of file paths and returns a set of unique, normalized paths.

        Args:
            file_paths (List[str]): A list of file paths to normalize.

        Returns:
            Set[str]: A set of unique, normalized absolute file paths.
        """
        normalized_set = set()
        if not file_paths:
            return normalized_set

        for path in file_paths:
            normalized_path = self._normalize_path(path)
            if normalized_path:
                normalized_set.add(normalized_path)
        return normalized_set

    def detect_conflicts(self, tasks_data: List[Dict[str, Union[str, List[str]]]]) -> Dict[str, Any]:
        """
        Detects file conflicts among a list of tasks.

        A conflict occurs if two or more tasks declare the same file as editable.

        This method respects the `enable_conflict_detection` setting from the Config.
        It also enforces a timeout (in seconds) specified by `conflict_detection_timeout`.

        Args:
            tasks_data (List[Dict[str, Union[str, List[str]]]]): A list of dictionaries,
                where each dictionary represents a task and must contain:
                - 'task_id' (str): A unique identifier for the task.
                - 'editable_files' (List[str]): A list of file paths that the task intends to modify.

        Returns:
            Dict[str, Any]: A dictionary containing conflict detection results:
                - 'has_conflicts' (bool): True if any conflicts were detected, False otherwise.
                - 'conflicting_files' (Dict[str, List[str]]): A dictionary where keys are
                  normalized file paths that are in conflict, and values are lists of
                  'task_id's that declare that file as editable.
                - 'conflict_matrix' (Dict[Tuple[str, str], List[str]]): A dictionary where
                  keys are tuples of (task_id1, task_id2) representing a pair of conflicting
                  tasks, and values are lists of normalized file paths they both intend to modify.
                - 'timed_out' (bool): True if the detection timed out, False otherwise.
        """
        if not self.enable_conflict_detection:
            if self.enable_conflict_logging:
                logger.info("Conflict detection is disabled via configuration.")
            return {
                "has_conflicts": False,
                "conflicting_files": {},
                "conflict_matrix": {},
                "timed_out": False,
            }

        if not tasks_data:
            if self.enable_conflict_logging:
                logger.info("No tasks provided for conflict detection.")
            return {
                "has_conflicts": False,
                "conflicting_files": {},
                "conflict_matrix": {},
                "timed_out": False,
            }

        start_time = time.time()

        task_file_map: Dict[str, Set[str]] = {}
        file_task_map: Dict[str, List[str]] = defaultdict(list)
        
        # Normalize paths for each task and build initial mappings
        for task in tasks_data:
            if time.time() - start_time > self.conflict_detection_timeout:
                if self.enable_conflict_logging:
                    logger.warning("Conflict detection timed out.")
                return {
                    "has_conflicts": False,
                    "conflicting_files": {},
                    "conflict_matrix": {},
                    "timed_out": True,
                }

            task_id = str(task.get("task_id")) # Ensure task_id is string for consistency
            editable_files = task.get("editable_files", [])
            
            if not isinstance(editable_files, list):
                if self.enable_conflict_logging:
                    logger.warning(f"Task '{task_id}' has 'editable_files' that is not a list. Skipping.")
                continue

            normalized_files = self._normalize_paths_list(editable_files)
            task_file_map[task_id] = normalized_files

            for n_file in normalized_files:
                file_task_map[n_file].append(task_id)

        conflicting_files: Dict[str, List[str]] = {}
        has_conflicts = False

        # Identify files that are part of conflicts
        for n_file, task_ids in file_task_map.items():
            if len(task_ids) > 1:
                conflicting_files[n_file] = sorted(task_ids)
                has_conflicts = True

        conflict_matrix: Dict[Tuple[str, str], List[str]] = defaultdict(list)

        # Build the conflict matrix
        task_ids_list = list(task_file_map.keys())
        for i in range(len(task_ids_list)):
            for j in range(i + 1, len(task_ids_list)):
                if time.time() - start_time > self.conflict_detection_timeout:
                    if self.enable_conflict_logging:
                        logger.warning("Conflict detection timed out during matrix building.")
                    return {
                        "has_conflicts": has_conflicts,
                        "conflicting_files": conflicting_files,
                        "conflict_matrix": dict(conflict_matrix),
                        "timed_out": True,
                    }

                task_id1 = task_ids_list[i]
                task_id2 = task_ids_list[j]

                files1 = task_file_map.get(task_id1, set())
                files2 = task_file_map.get(task_id2, set())

                common_files = sorted(list(files1.intersection(files2)))
                if common_files:
                    conflict_matrix[(task_id1, task_id2)] = common_files

        if self.enable_conflict_logging:
            logger.info(f"Conflict detection complete. Conflicts found: {has_conflicts}")
        return {
            "has_conflicts": has_conflicts,
            "conflicting_files": conflicting_files,
            "conflict_matrix": dict(conflict_matrix), # Convert defaultdict to dict for final output
            "timed_out": False,
        }

    def generate_conflict_report(self, conflicts_data: Dict[str, Any], verbosity: Optional[str] = None) -> str:
        """
        Generates a human-readable report from the conflict detection results.

        Supports verbosity levels:
        - minimal: Only summary of conflicting files.
        - standard: Summary + detailed conflict matrix + recommendations.
        - verbose: Includes all standard info plus detailed task-file mappings.

        Args:
            conflicts_data (Dict[str, Any]): The output dictionary from `detect_conflicts`.
            verbosity (Optional[str]): Verbosity level to override configuration setting.
                                       One of 'minimal', 'standard', 'verbose'.

        Returns:
            str: A formatted string detailing the conflicts.
        """
        if verbosity is None:
            verbosity = self.conflict_report_verbosity
        verbosity = verbosity.lower()
        if verbosity not in {"minimal", "standard", "verbose"}:
            verbosity = "standard"

        report_lines = []
        has_conflicts = conflicts_data.get("has_conflicts", False)
        conflicting_files = conflicts_data.get("conflicting_files", {})
        conflict_matrix = conflicts_data.get("conflict_matrix", {})
        timed_out = conflicts_data.get("timed_out", False)

        report_lines.append("--- File Conflict Report ---")

        if timed_out:
            report_lines.append("WARNING: Conflict detection timed out before completion.")
            if self.enable_conflict_logging:
                logger.warning("Conflict report generated with timeout warning.")

        if not has_conflicts:
            report_lines.append("No file conflicts detected among the provided tasks. Parallel execution is safe.")
            if self.enable_conflict_logging:
                logger.info("Generated conflict report: No conflicts.")
            return "\n".join(report_lines)

        report_lines.append("WARNING: File conflicts detected! Parallel execution may lead to unexpected behavior or data loss.")

        if verbosity in {"minimal", "standard", "verbose"}:
            report_lines.append("\nSummary of Conflicting Files:")
            for file_path, task_ids in conflicting_files.items():
                report_lines.append(f"- File: '{file_path}' is editable by tasks: {', '.join(task_ids)}")

        if verbosity in {"standard", "verbose"}:
            report_lines.append("\nDetailed Conflict Matrix (Task Pairs and Overlapping Files):")
            if not conflict_matrix:
                report_lines.append("  No direct task-pair conflicts found, but individual files are shared.")
            else:
                for (task1, task2), files in conflict_matrix.items():
                    report_lines.append(f"- Tasks '{task1}' and '{task2}' conflict on files:")
                    for f in files:
                        report_lines.append(f"    - {f}")

            report_lines.append("\nRecommendations:")
            report_lines.append("1. Review the conflicting files and tasks to understand the dependencies.")
            report_lines.append("2. Consider executing conflicting tasks sequentially instead of in parallel.")
            report_lines.append("3. Refactor tasks to minimize shared editable files if possible.")
            report_lines.append("4. Implement a robust merge strategy or manual review process for conflicting changes.")
            report_lines.append("\n--- End of Report ---")

        if verbosity == "verbose":
            report_lines.append("\nVerbose Details:")
            # Note: task_file_map is not directly stored in conflicts_data output from detect_conflicts
            # If this detail is needed, detect_conflicts would need to return it.
            # For now, this section will likely be empty unless conflicts_data is augmented elsewhere.
            # Keeping it for consistency with original verbose intent.
            all_tasks_data = conflicts_data.get("all_tasks_data", []) # Placeholder if full task data is passed
            if all_tasks_data:
                report_lines.append("\nAll Task File Mappings:")
                for task_item in all_tasks_data:
                    task_id = task_item.get("task_id")
                    editable_files = task_item.get("editable_files")
                    if task_id and editable_files:
                        report_lines.append(f"Task '{task_id}' edits files:")
                        for f in sorted(editable_files):
                            report_lines.append(f"  - {f}")


        if self.enable_conflict_logging:
            logger.warning("Generated conflict report: Conflicts detected.")
        return "\n".join(report_lines)

    def get_conflicting_files(self, conflicts_data: Dict[str, Any]) -> Set[str]:
        """
        Extracts a set of all unique file paths that are part of any conflict.

        Args:
            conflicts_data (Dict[str, Any]): The output dictionary from `detect_conflicts`.

        Returns:
            Set[str]: A set of normalized file paths that are in conflict.
        """
        return set(conflicts_data.get("conflicting_files", {}).keys())

    def get_tasks_for_file(self, conflicts_data: Dict[str, Any], file_path: str) -> List[str]:
        """
        Returns a list of task IDs that conflict on a specific file.

        Args:
            conflicts_data (Dict[str, Any]): The output dictionary from `detect_conflicts`.
            file_path (str): The (potentially unnormalized) file path to check.

        Returns:
            List[str]: A sorted list of task IDs that modify the given file,
                       or an empty list if the file is not in conflict or not found.
        """
        normalized_path = self._normalize_path(file_path)
        if normalized_path:
            return sorted(conflicts_data.get("conflicting_files", {}).get(normalized_path, []))
        return []

# Example Usage (for testing purposes, can be removed in final integration)
if __name__ == "__main__":
    # Create some dummy files for testing path normalization and symlinks
    # In a real scenario, these would already exist in your project
    current_dir = Path.cwd()
    test_dir = current_dir / "test_conflict_detection"
    test_dir.mkdir(exist_ok=True)

    (test_dir / "fileA.py").write_text("print('A')")
    (test_dir / "fileB.js").write_text("console.log('B');")
    (test_dir / "subdir").mkdir(exist_ok=True)
    (test_dir / "subdir" / "fileC.txt").write_text("Content C")
    
    # Create a symlink
    symlink_target = test_dir / "fileA.py"
    symlink_path = test_dir / "link_to_A.py"
    if symlink_path.exists():
        symlink_path.unlink() # Remove existing symlink if any
    os.symlink(symlink_target, symlink_path)

    print(f"Created test files in: {test_dir}")

    detector = FileConflictDetector(working_dir=str(test_dir))

    tasks_to_check = [
        {
            "task_id": "Task-1",
            "editable_files": [
                "fileA.py",
                "subdir/fileC.txt",
                "non_existent_file.py" # Should be handled gracefully
            ],
        },
        {
            "task_id": "Task-2",
            "editable_files": [
                "fileA.py",  # Conflict with Task-1
                "fileB.js",
                str(symlink_path) # Should resolve to fileA.py, causing another conflict
            ],
        },
        {
            "task_id": "Task-3",
            "editable_files": [
                "fileB.js",  # Conflict with Task-2
                "new_feature.py"
            ],
        },
        {
            "task_id": "Task-4",
            "editable_files": [
                "another_file.txt" # No conflicts
            ],
        },
        {
            "task_id": "Task-5",
            "editable_files": [] # Empty list, should be handled
        },
        {
            "task_id": "Task-6",
            "editable_files": None # None value, should be handled
        }
    ]

    print("\n--- Running Conflict Detection ---")
    conflicts = detector.detect_conflicts(tasks_to_check)
    print("\n--- Raw Conflict Data ---")
    import json
    print(json.dumps(conflicts, indent=2))

    print("\n--- Conflict Report (Standard Verbosity) ---")
    report = detector.generate_conflict_report(conflicts)
    print(report)

    print("\n--- Conflict Report (Verbose Verbosity) ---")
    # To make verbose report show task_file_map, we need to pass original tasks_to_check
    # This is a slight deviation from original, but makes verbose output meaningful.
    conflicts_verbose = conflicts.copy()
    conflicts_verbose["all_tasks_data"] = tasks_to_check 
    report_verbose = detector.generate_conflict_report(conflicts_verbose, verbosity="verbose")
    print(report_verbose)

    print("\n--- Helper Function Tests ---")
    conflicting_files_set = detector.get_conflicting_files(conflicts)
    print(f"All conflicting files: {conflicting_files_set}")

    tasks_for_fileA = detector.get_tasks_for_file(conflicts, "fileA.py")
    print(f"Tasks modifying fileA.py: {tasks_for_fileA}")

    tasks_for_fileB = detector.get_tasks_for_file(conflicts, str(test_dir / "fileB.js"))
    print(f"Tasks modifying {test_dir / 'fileB.js'}: {tasks_for_fileB}")

    tasks_for_non_conflict_file = detector.get_tasks_for_file(conflicts, "another_file.txt")
    print(f"Tasks modifying another_file.txt: {tasks_for_non_conflict_file}")

    tasks_for_non_existent_file = detector.get_tasks_for_file(conflicts, "definitely_not_here.py")
    print(f"Tasks modifying definitely_not_here.py: {tasks_for_non_existent_file}")

    # Clean up dummy files
    try:
        os.remove(test_dir / "fileA.py")
        os.remove(test_dir / "fileB.js")
        os.remove(test_dir / "subdir" / "fileC.txt")
        os.rmdir(test_dir / "subdir")
        os.remove(symlink_path)
        os.rmdir(test_dir)
        print(f"\nCleaned up test directory: {test_dir}")
    except OSError as e:
        print(f"\nError cleaning up test directory: {e}")
