"""Configuration handler

This module provides YAML-based configuration management for the chord generator, including:
- General parameters (keyboard layout, input/output paths)
- Debug settings (logging level, debug output)
- Performance benchmarking options
- Metric weights (standalone, assignment, and set metrics)
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from src.common.shared_types import (
    AssignmentMetricType,
    Finger,
    SetMetricType,
    StandaloneMetricType,
)


class LogLevel(Enum):
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG


@dataclass
class Paths:
    """Path configuration for input and output files"""

    # Base directories
    base_dir: Path
    data_dir: Path

    # Input directories
    key_layouts_dir: Path
    corpuses_dir: Path
    tokens_dir: Path

    # Output directories
    chords_dir: Path
    debug_dir: Path
    results_dir: Path
    cache_dir: Path

    def __post_init__(self):
        """Create directories if they don't exist"""
        for dir_path in [
            self.data_dir,
            self.key_layouts_dir,
            self.corpuses_dir,
            self.tokens_dir,
            self.chords_dir,
            self.debug_dir,
            self.results_dir,
            self.cache_dir,
        ]:
            os.makedirs(dir_path, exist_ok=True)

    def get_layout_path(self, layout_file: str) -> Path:
        """Get path to a specific layout file"""
        layout_path = self.key_layouts_dir / layout_file
        if not layout_path.exists():
            raise ValueError(f"Layout file not found: {layout_path}")
        return layout_path

    def get_corpus_path(self, corpus_file: str) -> Path:
        """Get path to a specific corpus file"""
        corpus_path = self.corpuses_dir / corpus_file
        if not corpus_path.exists():
            raise ValueError(f"Corpus file not found: {corpus_path}")
        return corpus_path

    def get_tokens_path(self, tokens_file: str) -> Path:
        """Get path to a specific tokens file"""
        tokens_path = self.tokens_dir / tokens_file
        if not tokens_path.exists():
            raise ValueError(f"Tokens file not found: {tokens_path}")
        return tokens_path

    def get_log_path(self, log_file: str) -> Path:
        """Get path for a log file"""
        return self.debug_dir / log_file


@dataclass
class DebugOptions:
    """Debug and logging options"""

    enabled: bool
    log_level: LogLevel
    log_file: Optional[str]  # Just the filename, not the full path
    print_cost_details: bool
    save_intermediate_results: bool


@dataclass
class BenchmarkOptions:
    """Performance benchmarking configuration"""

    enabled: bool
    track_individual_metrics: bool
    visual_update_interval: int


@dataclass
class ChordGeneration:
    """Chord generation parameters"""

    min_letter_count: int
    max_letter_count: int
    allow_non_adjacent_keys: bool


@dataclass
class CorpusGenerationConfig:
    """Corpus generation parameters"""

    sample_size: int
    min_length: int
    max_length: int
    total_corpus_size: int
    categories: Dict[str, float]
    api_keys: Dict[str, str]


@dataclass
class StandaloneWeights:
    """Weights for standalone metrics"""

    weights: Dict[StandaloneMetricType, float]


@dataclass
class AssignmentWeights:
    """Weights for assignment metrics"""

    weights: Dict[AssignmentMetricType, float]


@dataclass
class SetWeights:
    """Weights for set metrics"""

    weights: Dict[SetMetricType, float]


@dataclass
class TokenAnalysisConfig:
    """Configuration for token analysis"""

    min_token_length: int
    max_token_length: int
    top_n_tokens: int
    include_characters: bool
    include_character_ngrams: bool
    include_words: bool
    include_word_ngrams: bool
    use_parallel_processing: bool


@dataclass
class ChordAssignmentConfig:
    """Configuration for chord assignment algorithms"""

    algorithm: str
    first_letter_unmatched_weight: float
    second_letter_unmatched_weight: float
    last_letter_unmatched_weight: float
    additional_letter_weight: float
    fallback_letter_weight: float
    vertical_stretch_weight: float
    vertical_pinch_weight: float
    horizontal_stretch_weight: float
    horizontal_pinch_weight: float
    diagonal_stretch_weight: float
    diagonal_pinch_weight: float
    same_finger_double_weight: float
    same_finger_triple_weight: float
    pinky_ring_stretch_weight: float
    ring_middle_scissor_weight: float
    middle_index_stretch_weight: float


@dataclass
class GeneratorConfig:
    """Main configuration for the chord generator"""

    # Core components
    paths: Paths
    debug: DebugOptions
    benchmark: BenchmarkOptions

    # Generation parameters
    chord_generation: ChordGeneration
    corpus_generation: CorpusGenerationConfig

    # Weights
    standalone_weights: StandaloneWeights
    assignment_weights: AssignmentWeights
    set_weights: SetWeights

    # Module-specific configs
    token_analysis: TokenAnalysisConfig
    chord_assignment: ChordAssignmentConfig

    # Current active settings - these are explicitly required with file extensions
    active_layout_file: str
    active_corpus_file: str
    active_tokens_file: str

    @classmethod
    def load_config(
        cls, config_path: Optional[Union[str, Path]] = None
    ) -> "GeneratorConfig":
        """Load configuration from YAML file

        Args:
            config_path: Optional path to config file. If None, uses default path.

        Returns:
            Loaded configuration object

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config values are invalid
        """
        if config_path is None:
            config_path = Path("data/config.yaml")

        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # Convert YAML data to GeneratorConfig
        return cls._from_dict(config_data)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "GeneratorConfig":
        """Create config from dictionary"""
        # Check for required top-level sections
        required_sections = [
            "paths",
            "debug",
            "benchmark",
            "chord_generation",
            "corpus_generation",
            "standalone_weights",
            "assignment_weights",
            "set_weights",
            "token_analysis",
            "chord_assignment",
            "active_layout_file",
            "active_corpus_file",
            "active_tokens_file",
        ]

        for section in required_sections:
            if section not in data:
                raise ValueError(f"Missing required configuration section: {section}")

        # Parse paths section
        paths_data = data["paths"]
        required_path_fields = [
            "base_dir",
            "data_dir",
            "key_layouts_dir",
            "corpuses_dir",
            "tokens_dir",
            "chords_dir",
            "debug_dir",
            "results_dir",
            "cache_dir",
        ]
        for field in required_path_fields:
            if field not in paths_data:
                raise ValueError(f"Missing required path field: {field}")

        paths = Paths(
            base_dir=Path(paths_data["base_dir"]),
            data_dir=Path(paths_data["data_dir"]),
            key_layouts_dir=Path(paths_data["key_layouts_dir"]),
            corpuses_dir=Path(paths_data["corpuses_dir"]),
            tokens_dir=Path(paths_data["tokens_dir"]),
            chords_dir=Path(paths_data["chords_dir"]),
            debug_dir=Path(paths_data["debug_dir"]),
            results_dir=Path(paths_data["results_dir"]),
            cache_dir=Path(paths_data["cache_dir"]),
        )

        # Parse debug options
        debug_data = data["debug"]
        debug = DebugOptions(
            enabled=debug_data["enabled"],
            log_level=LogLevel[debug_data["log_level"]],
            log_file=debug_data.get("log_file"),
            print_cost_details=debug_data["print_cost_details"],
            save_intermediate_results=debug_data["save_intermediate_results"],
        )

        # Parse benchmark options
        bench_data = data["benchmark"]
        benchmark = BenchmarkOptions(
            enabled=bench_data["enabled"],
            track_individual_metrics=bench_data["track_individual_metrics"],
            visual_update_interval=bench_data["visual_update_interval"],
        )

        # Parse chord generation
        gen_data = data["chord_generation"]
        chord_generation = ChordGeneration(
            min_letter_count=gen_data["min_letter_count"],
            max_letter_count=gen_data["max_letter_count"],
            allow_non_adjacent_keys=gen_data["allow_non_adjacent_keys"],
        )

        # Parse corpus generation
        corpus_data = data["corpus_generation"]
        corpus_generation = CorpusGenerationConfig(
            sample_size=corpus_data["sample_size"],
            min_length=corpus_data["min_length"],
            max_length=corpus_data["max_length"],
            total_corpus_size=corpus_data["total_corpus_size"],
            categories=corpus_data["categories"],
            api_keys=corpus_data["api_keys"],
        )

        # Parse standalone weights
        standalone_weights_data = data["standalone_weights"]
        standalone_weights = StandaloneWeights(
            weights={
                StandaloneMetricType[key]: float(value)
                for key, value in standalone_weights_data.items()
            }
        )

        # Parse assignment weights
        assignment_weights_data = data["assignment_weights"]
        assignment_weights = AssignmentWeights(
            weights={
                AssignmentMetricType[key]: float(value)
                for key, value in assignment_weights_data.items()
            }
        )

        # Parse set weights
        set_weights_data = data["set_weights"]
        set_weights = SetWeights(
            weights={
                SetMetricType[key]: float(value)
                for key, value in set_weights_data.items()
            }
        )

        # Parse token analysis config
        token_data = data["token_analysis"]
        token_analysis = TokenAnalysisConfig(
            min_token_length=token_data["min_token_length"],
            max_token_length=token_data["max_token_length"],
            top_n_tokens=token_data["top_n_tokens"],
            include_characters=token_data["include_characters"],
            include_character_ngrams=token_data["include_character_ngrams"],
            include_words=token_data["include_words"],
            include_word_ngrams=token_data["include_word_ngrams"],
            use_parallel_processing=token_data["use_parallel_processing"],
        )

        # Parse chord assignment config
        assign_data = data["chord_assignment"]
        chord_assignment = ChordAssignmentConfig(
            algorithm=assign_data["algorithm"],
            first_letter_unmatched_weight=assign_data["first_letter_unmatched_weight"],
            second_letter_unmatched_weight=assign_data[
                "second_letter_unmatched_weight"
            ],
            last_letter_unmatched_weight=assign_data["last_letter_unmatched_weight"],
            additional_letter_weight=assign_data["additional_letter_weight"],
            fallback_letter_weight=assign_data["fallback_letter_weight"],
            vertical_stretch_weight=assign_data["vertical_stretch_weight"],
            vertical_pinch_weight=assign_data["vertical_pinch_weight"],
            horizontal_stretch_weight=assign_data["horizontal_stretch_weight"],
            horizontal_pinch_weight=assign_data["horizontal_pinch_weight"],
            diagonal_stretch_weight=assign_data["diagonal_stretch_weight"],
            diagonal_pinch_weight=assign_data["diagonal_pinch_weight"],
            same_finger_double_weight=assign_data["same_finger_double_weight"],
            same_finger_triple_weight=assign_data["same_finger_triple_weight"],
            pinky_ring_stretch_weight=assign_data["pinky_ring_stretch_weight"],
            ring_middle_scissor_weight=assign_data["ring_middle_scissor_weight"],
            middle_index_stretch_weight=assign_data["middle_index_stretch_weight"],
        )

        # Get active settings with file extensions
        active_layout_file = data["active_layout_file"]
        active_corpus_file = data["active_corpus_file"]
        active_tokens_file = data["active_tokens_file"]

        # Build the complete config
        return cls(
            paths=paths,
            debug=debug,
            benchmark=benchmark,
            chord_generation=chord_generation,
            corpus_generation=corpus_generation,
            standalone_weights=standalone_weights,
            assignment_weights=assignment_weights,
            set_weights=set_weights,
            token_analysis=token_analysis,
            chord_assignment=chord_assignment,
            active_layout_file=active_layout_file,
            active_corpus_file=active_corpus_file,
            active_tokens_file=active_tokens_file,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for YAML serialization"""
        # Create a dictionary with all configuration sections
        result = {
            "active_layout_file": self.active_layout_file,
            "active_corpus_file": self.active_corpus_file,
            "active_tokens_file": self.active_tokens_file,
            "paths": {
                "base_dir": str(self.paths.base_dir),
                "data_dir": str(self.paths.data_dir),
                "key_layouts_dir": str(self.paths.key_layouts_dir),
                "corpuses_dir": str(self.paths.corpuses_dir),
                "tokens_dir": str(self.paths.tokens_dir),
                "chords_dir": str(self.paths.chords_dir),
                "debug_dir": str(self.paths.debug_dir),
                "results_dir": str(self.paths.results_dir),
                "cache_dir": str(self.paths.cache_dir),
            },
            "debug": {
                "enabled": self.debug.enabled,
                "log_level": self.debug.log_level.name,
                "log_file": self.debug.log_file,
                "print_cost_details": self.debug.print_cost_details,
                "save_intermediate_results": self.debug.save_intermediate_results,
            },
            "benchmark": {
                "enabled": self.benchmark.enabled,
                "track_individual_metrics": self.benchmark.track_individual_metrics,
                "visual_update_interval": self.benchmark.visual_update_interval,
            },
            "chord_generation": {
                "min_letter_count": self.chord_generation.min_letter_count,
                "max_letter_count": self.chord_generation.max_letter_count,
                "allow_non_adjacent_keys": self.chord_generation.allow_non_adjacent_keys,
            },
            "corpus_generation": {
                "sample_size": self.corpus_generation.sample_size,
                "min_length": self.corpus_generation.min_length,
                "max_length": self.corpus_generation.max_length,
                "total_corpus_size": self.corpus_generation.total_corpus_size,
                "categories": self.corpus_generation.categories,
                "api_keys": self.corpus_generation.api_keys,
            },
            "standalone_weights": {
                metric_type.name: weight
                for metric_type, weight in self.standalone_weights.weights.items()
            },
            "assignment_weights": {
                metric_type.name: weight
                for metric_type, weight in self.assignment_weights.weights.items()
            },
            "set_weights": {
                metric_type.name: weight
                for metric_type, weight in self.set_weights.weights.items()
            },
            "token_analysis": {
                "min_token_length": self.token_analysis.min_token_length,
                "max_token_length": self.token_analysis.max_token_length,
                "top_n_tokens": self.token_analysis.top_n_tokens,
                "include_characters": self.token_analysis.include_characters,
                "include_character_ngrams": self.token_analysis.include_character_ngrams,
                "include_words": self.token_analysis.include_words,
                "include_word_ngrams": self.token_analysis.include_word_ngrams,
                "use_parallel_processing": self.token_analysis.use_parallel_processing,
            },
            "chord_assignment": {
                "algorithm": self.chord_assignment.algorithm,
                "first_letter_unmatched_weight": self.chord_assignment.first_letter_unmatched_weight,
                "second_letter_unmatched_weight": self.chord_assignment.second_letter_unmatched_weight,
                "last_letter_unmatched_weight": self.chord_assignment.last_letter_unmatched_weight,
                "additional_letter_weight": self.chord_assignment.additional_letter_weight,
                "fallback_letter_weight": self.chord_assignment.fallback_letter_weight,
                "vertical_stretch_weight": self.chord_assignment.vertical_stretch_weight,
                "vertical_pinch_weight": self.chord_assignment.vertical_pinch_weight,
                "horizontal_stretch_weight": self.chord_assignment.horizontal_stretch_weight,
                "horizontal_pinch_weight": self.chord_assignment.horizontal_pinch_weight,
                "diagonal_stretch_weight": self.chord_assignment.diagonal_stretch_weight,
                "diagonal_pinch_weight": self.chord_assignment.diagonal_pinch_weight,
                "same_finger_double_weight": self.chord_assignment.same_finger_double_weight,
                "same_finger_triple_weight": self.chord_assignment.same_finger_triple_weight,
                "pinky_ring_stretch_weight": self.chord_assignment.pinky_ring_stretch_weight,
                "ring_middle_scissor_weight": self.chord_assignment.ring_middle_scissor_weight,
                "middle_index_stretch_weight": self.chord_assignment.middle_index_stretch_weight,
            },
        }
        return result

    def save_config(self, config_path: Union[str, Path]) -> None:
        """Save configuration to YAML file"""
        config_path = Path(config_path)

        # Create parent directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    def setup_logging(self) -> None:
        """Configure logging based on debug settings"""
        if not self.debug.enabled:
            return

        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Ensure log directory exists
        if self.debug.log_file:
            log_path = self.paths.get_log_path(self.debug.log_file)
            log_dir = log_path.parent
            os.makedirs(log_dir, exist_ok=True)

            logging.basicConfig(
                level=self.debug.log_level.value,
                format=log_format,
                handlers=[
                    logging.FileHandler(log_path),
                    logging.StreamHandler(),
                ],
            )
        else:
            logging.basicConfig(level=self.debug.log_level.value, format=log_format)

    def validate(self) -> None:
        """Validate configuration values

        Raises:
            ValueError: If any configuration values are invalid
        """
        # Validate chord generation settings
        if self.chord_generation.min_letter_count < 1:
            raise ValueError("min_letter_count must be at least 1")
        if (
            self.chord_generation.max_letter_count
            < self.chord_generation.min_letter_count
        ):
            raise ValueError(
                "max_letter_count must be greater than or equal to min_letter_count"
            )

        # Validate token analysis settings
        if self.token_analysis.min_token_length < 1:
            raise ValueError("min_token_length must be at least 1")
        if self.token_analysis.max_token_length < self.token_analysis.min_token_length:
            raise ValueError(
                "max_token_length must be greater than or equal to min_token_length"
            )
        if self.token_analysis.top_n_tokens < 1:
            raise ValueError("top_n_tokens must be at least 1")

        # Validate corpus generation settings
        if self.corpus_generation.min_length < 1:
            raise ValueError("min_length must be at least 1")
        if self.corpus_generation.max_length < self.corpus_generation.min_length:
            raise ValueError("max_length must be greater than or equal to min_length")
        if self.corpus_generation.sample_size < 1:
            raise ValueError("sample_size must be at least 1")
        if self.corpus_generation.total_corpus_size < 1:
            raise ValueError("total_corpus_size must be at least 1")
        if not self.corpus_generation.categories:
            raise ValueError("categories must not be empty")
        if sum(self.corpus_generation.categories.values()) <= 0:
            raise ValueError("sum of category weights must be positive")

        # Validate active settings by checking that the referenced files exist
        try:
            self.paths.get_layout_path(self.active_layout_file)
        except Exception as e:
            raise ValueError(f"Invalid active_layout_file: {e}")

        try:
            self.paths.get_corpus_path(self.active_corpus_file)
        except Exception as e:
            raise ValueError(f"Invalid active_corpus_file: {e}")

        try:
            self.paths.get_tokens_path(self.active_tokens_file)
        except Exception as e:
            raise ValueError(f"Invalid active_tokens_file: {e}")
