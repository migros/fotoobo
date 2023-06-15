"""
Test the results helper class
"""


from pathlib import Path
from typing import Dict

from fotoobo.helpers.result import Result


class TestResults:
    """Test the results class"""

    def test_save_with_template(self, temp_dir: Path) -> None:
        """Test save_with_template"""
        result = Result[Dict[str, Dict[str, int]]]()
        result.push_result("dummy_ems", {"fotoobo": {"dummy_var": 42}})
        output_file = temp_dir / "output.txt"
        result.save_with_template("dummy_ems", Path("tests/data/dummy.j2"), output_file)
        assert output_file.is_file()
        content = output_file.read_text(encoding="UTF-8")
        assert "dummy" in content
        assert "42" in content
