"""Configuration."""
from typing import Optional


# pylint: disable=too-few-public-methods
class Config:
    """Main configuration state."""

    def __init__(self, **kwargs):
        """Class constructor."""
        self.prog: Optional[str] = kwargs.get("prog", None)

        self.color: Optional[bool] = kwargs.get("color", None)
        self.force_wide: Optional[bool] = kwargs.get("force_wide", None)
        self.quiet: Optional[bool] = kwargs.get("quiet", None)
        self.verbose: Optional[int] = kwargs.get("verbose", None)
