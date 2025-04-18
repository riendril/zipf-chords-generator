"""Types shared across the chord generator modules"""

import json
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class KeyPosition:
    """Position and finger assignment of a key on the input device"""

    finger: "Finger"
    vertical_distance_to_resting_position: int
    horizontal_distance_to_resting_position: int
    finger_to_left: Optional["Finger"] = None
    finger_to_right: Optional["Finger"] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "finger": self.finger.name if self.finger else None,
            "vertical_distance": self.vertical_distance_to_resting_position,
            "horizontal_distance": self.horizontal_distance_to_resting_position,
            "finger_to_left": self.finger_to_left.name if self.finger_to_left else None,
            "finger_to_right": (
                self.finger_to_right.name if self.finger_to_right else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], finger_enum: type) -> "KeyPosition":
        """Create from dictionary after JSON deserialization"""
        return cls(
            finger=finger_enum[data["finger"]] if data["finger"] else None,
            vertical_distance_to_resting_position=data["vertical_distance"],
            horizontal_distance_to_resting_position=data["horizontal_distance"],
            finger_to_left=(
                finger_enum[data["finger_to_left"]] if data["finger_to_left"] else None
            ),
            finger_to_right=(
                finger_enum[data["finger_to_right"]]
                if data["finger_to_right"]
                else None
            ),
        )


class Finger(Enum):
    """Enum for fingers that can be assigned to keys"""

    L_PINKY = auto()
    L_RING = auto()
    L_MIDDLE = auto()
    L_INDEX = auto()
    L_THUMB = auto()
    R_THUMB = auto()
    R_INDEX = auto()
    R_MIDDLE = auto()
    R_RING = auto()
    R_PINKY = auto()


@dataclass
class WordData:
    """Represents preprocessed data for a word"""

    original: str
    lower: str
    length: int
    zipf_weight: float
    frequency: int = 0  # Added for word frequency count
    rank: int = 0  # Added for word frequency rank
    score: float = 0.0  # Added for token score
    difficulty: float = 0.0  # Added for typing difficulty

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "original": self.original,
            "lower": self.lower,
            "length": self.length,
            "zipf_weight": self.zipf_weight,
            "frequency": self.frequency,
            "rank": self.rank,
            "score": self.score,
            "difficulty": self.difficulty,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WordData":
        """Create from dictionary after JSON deserialization"""
        return cls(
            original=data["original"],
            lower=data["lower"],
            length=data["length"],
            zipf_weight=data.get("zipf_weight", 0.0),
            frequency=data.get("frequency", 0),
            rank=data.get("rank", 0),
            score=data.get("score", 0.0),
            difficulty=data.get("difficulty", 0.0),
        )

    @classmethod
    def from_word(
        cls,
        word: str,
        frequency: int = 0,
        rank: int = 0,
        zipf_weight: float = 0.0,
        score: float = 0.0,
        difficulty: float = 0.0,
    ) -> "WordData":
        """Create from a word string with optional frequency information"""
        return cls(
            original=word,
            lower=word.lower(),
            length=len(word),
            zipf_weight=zipf_weight,
            frequency=frequency,
            rank=rank,
            score=score,
            difficulty=difficulty,
        )


@dataclass
class ChordData:
    """Represents preprocessed data for a chord"""

    letters: str
    keys: Tuple[KeyPosition, ...] = field(default_factory=tuple)
    length: int = field(init=False)

    def __post_init__(self):
        self.length = len(self.letters)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "letters": self.letters,
            "keys": [key.to_dict() for key in self.keys],
            "length": self.length,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], finger_enum: type = Finger) -> "ChordData":
        """Create from dictionary after JSON deserialization"""
        instance = cls(
            letters=data["letters"],
            keys=tuple(
                KeyPosition.from_dict(key_data, finger_enum)
                for key_data in data.get("keys", [])
            ),
        )
        # Ensure length is set properly even if it was provided in the data
        instance.length = len(instance.letters)
        return instance

    @classmethod
    def from_letters(cls, letters: str) -> "ChordData":
        """Create from a string of letters without key positions"""
        return cls(letters=letters)


@dataclass
class Assignment:
    """Represents a word-chord assignment pair"""

    word: WordData
    chord: ChordData
    score: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "word": self.word.to_dict(),
            "chord": self.chord.to_dict(),
            "score": self.score,
            "metrics": self.metrics,
        }

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], finger_enum: type = Finger
    ) -> "Assignment":
        """Create from dictionary after JSON deserialization"""
        return cls(
            word=WordData.from_dict(data["word"]),
            chord=ChordData.from_dict(data["chord"], finger_enum),
            score=data.get("score", 0.0),
            metrics=data.get("metrics", {}),
        )


@dataclass
class AssignmentSet:
    """Represents a set of assignments between words and chords"""

    name: str
    assignments: List[Assignment] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "assignments": [assignment.to_dict() for assignment in self.assignments],
            "metrics": self.metrics,
        }

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], finger_enum: type = Finger
    ) -> "AssignmentSet":
        """Create from dictionary after JSON deserialization"""
        return cls(
            name=data["name"],
            assignments=[
                Assignment.from_dict(assignment_data, finger_enum)
                for assignment_data in data.get("assignments", [])
            ],
            metrics=data.get("metrics", {}),
        )

    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save assignment set to JSON file"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(
        cls, file_path: Union[str, Path], finger_enum: type = Finger
    ) -> "AssignmentSet":
        """Load assignment set from JSON file"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data, finger_enum)


class StandaloneMetricType(Enum):
    """Types of metrics for standalone chord analysis"""

    CHORD_LENGTH = auto()
    HORIZONTAL_PINCH = auto()
    HORIZONTAL_STRETCH = auto()
    VERTICAL_PINCH = auto()
    VERTICAL_STRETCH = auto()
    DIAGONAL_DOWNWARD_PINCH = auto()
    DIAGONAL_DOWNWARD_STRETCH = auto()
    DIAGONAL_UPWARD_PINCH = auto()
    DIAGONAL_UPWARD_STRETCH = auto()
    SAME_FINGER_DOUBLE_ADJACENT = auto()
    SAME_FINGER_DOUBLE_GAP = auto()
    SAME_FINGER_TRIPLE = auto()
    FULL_SCISSOR_DOUBLE = auto()
    FULL_SCISSOR_TRIPLE = auto()
    FULL_SCISSOR_QUADRUPLE = auto()
    FULL_SCISSOR_QUINTUPLE = auto()
    HALF_SCISSOR_DOUBLE = auto()
    HORIZONTAL_STRETCH_DOUBLE = auto()
    PINKY_RING_SCISSOR = auto()
    RING_INDEX_SCISSOR = auto()


class AssignmentMetricType(Enum):
    """Types of metrics for word-chord assignments"""

    FIRST_LETTER_UNMATCHED = auto()
    SECOND_LETTER_UNMATCHED = auto()
    LAST_LETTER_UNMATCHED = auto()
    PHONETIC_DISSIMILARITY = auto()
    EXTRA_LETTER = auto()


class SetMetricType(Enum):
    """Types of metrics for sets of assignments"""

    FINGER_UTILIZATION = auto()
    HAND_UTILIZATION = auto()
    CHORD_PATTERN_CONSISTENCY = auto()


@dataclass
class TokenCollection:
    """Collection of tokens with frequency information"""

    name: str
    tokens: List[WordData] = field(default_factory=list)
    ordered_by_frequency: bool = True
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "tokens": [token.to_dict() for token in self.tokens],
            "orderedByFrequency": self.ordered_by_frequency,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenCollection":
        """Create from dictionary after JSON deserialization"""
        return cls(
            name=data["name"],
            tokens=[
                WordData.from_dict(token_data) for token_data in data.get("tokens", [])
            ],
            ordered_by_frequency=data.get("orderedByFrequency", True),
            source=data.get("source"),
        )

    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save token collection to JSON file"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> "TokenCollection":
        """Load token collection from JSON file"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class ChordCollection:
    """Collection of chords with their properties"""

    name: str
    min_length: int
    max_length: int
    chords: List[ChordData] = field(default_factory=list)
    costs: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "chords": [chord.to_dict() for chord in self.chords],
            "costs": self.costs,
        }

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], finger_enum: type = Finger
    ) -> "ChordCollection":
        """Create from dictionary after JSON deserialization"""
        return cls(
            name=data["name"],
            min_length=data["min_length"],
            max_length=data["max_length"],
            chords=[
                ChordData.from_dict(chord_data, finger_enum)
                for chord_data in data.get("chords", [])
            ],
            costs=data.get("costs", {}),
        )

    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save chord collection to JSON file"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(
        cls, file_path: Union[str, Path], finger_enum: type = Finger
    ) -> "ChordCollection":
        """Load chord collection from JSON file"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data, finger_enum)
