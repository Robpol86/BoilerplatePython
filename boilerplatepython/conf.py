"""Configuration."""
from typing import Optional


# pylint: disable=too-few-public-methods
class Config:
    """Main configuration state."""

    def __init__(self, **kwargs):
        """Class constructor."""
        self.prog: Optional[str] = kwargs.get("prog", None)
        self.bell: Optional[bool] = kwargs.get("bell", None)
        self.color: Optional[bool] = kwargs.get("color", None)
        self.extended: Optional[int] = kwargs.get("extended", None)
        self.quiet: Optional[bool] = kwargs.get("quiet", None)
        self.verbose: Optional[int] = kwargs.get("verbose", None)
