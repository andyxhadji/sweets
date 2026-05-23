"""Daily reflections display mode."""

from datetime import date
from pathlib import Path
import random
from typing import Any

import yaml

from sweets.core.board import Board
from sweets.modes.base import Mode


class ReflectionsMode(Mode):
    """Display a daily reflection question."""

    name = "Daily Reflections"
    slug = "reflections"
    interval = 3600

    def __init__(self, rows: int = 6, cols: int = 22) -> None:
        super().__init__(rows, cols)
        self.reflections_path = Path("reflections.yaml")

    def render(self) -> Board:
        """Generate board with today's reflection."""
        reflections = self._load_reflections()

        if not reflections:
            return Board.from_text("ADD REFLECTIONS", rows=self.rows, cols=self.cols)

        today = date.today()
        rng = random.Random(today.toordinal())
        selected = reflections[rng.randrange(len(reflections))]

        return Board.from_text(selected, rows=self.rows, cols=self.cols)

    def _load_reflections(self) -> list[str]:
        """Load reflections from YAML file."""
        if not self.reflections_path.exists():
            return []

        try:
            with open(self.reflections_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError:
            return []

        if not data or not isinstance(data, list):
            return []

        return [str(item) for item in data]
