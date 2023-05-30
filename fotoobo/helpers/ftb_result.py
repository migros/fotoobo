"""
The FotooboResult class
"""
from typing import Any, Dict, List


class FotooboResult:
    """
    This class represents a FotooboResult dataset

    This dataset is meant to be the generic result structure for any tool inside fotoobo.
    It can then be rendered to some commandline output (CLI) or JSON response (REST API).
    """

    def __init__(self) -> None:
        """
        Create the FotooboResult object
        """
        # The devices where the processing has been successful
        self.successful: List[str] = []

        # The devices where the processing gave an error
        self.failed: List[str] = []

        # The total number of devices processed
        self.total: int = 0

        # Add messages for each device
        self.messages: Dict[str, List[str]] = {}

        # The results for each device
        self.results: Dict[str, Any] = {}

    def push_result(self, host: str, data: Any) -> None:
        """

        Args:
            host:
            data:

        Returns:

        """

        self.results[host] = data
