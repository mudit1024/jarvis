"""Tests for the commit-message rule: every commit must start with `JAR-<number>: <description>`.

Written BEFORE tools/commit_msg.py existed (TDD: RED -> GREEN -> REFACTOR).
"""

from pathlib import Path

import pytest

from tools.commit_msg import first_meaningful_line, is_valid_message, main


class TestIsValidMessage:
    @pytest.mark.parametrize(
        "message",
        [
            "JAR-2: add pre-commit hooks",
            "JAR-123: implement login with refresh tokens",
            "JAR-2: x",
        ],
    )
    def test_accepts_jira_key_colon_description(self, message: str) -> None:
        assert is_valid_message(message)

    @pytest.mark.parametrize(
        "message",
        [
            "Merge pull request #4 from mudit1024/feature/JAR-2-engineering-foundation",
            "Merge branch 'dev' into feature/JAR-5-registration",
            'Revert "JAR-2: add pre-commit hooks"',
        ],
    )
    def test_accepts_messages_git_writes_itself(self, message: str) -> None:
        assert is_valid_message(message)

    @pytest.mark.parametrize(
        "message",
        [
            "add pre-commit hooks",  # no key
            "jar-2: add hooks",  # key must be upper case
            "JAR-2 add hooks",  # missing colon
            "JAR-2:add hooks",  # missing space after colon
            "JAR-2:",  # no description
            "JAR-2:    ",  # description is only spaces
            "JAR-: add hooks",  # no number
            "SPLIT-2: add hooks",  # wrong project
            "",  # empty
        ],
    )
    def test_rejects_everything_else(self, message: str) -> None:
        assert not is_valid_message(message)


class TestFirstMeaningfulLine:
    def test_skips_git_comment_lines_and_blank_lines(self) -> None:
        text = "\n# Please enter the commit message\n\nJAR-2: add hooks\n\nLonger body.\n"
        assert first_meaningful_line(text) == "JAR-2: add hooks"

    def test_returns_empty_string_when_nothing_meaningful(self) -> None:
        assert first_meaningful_line("# only a comment\n\n") == ""


class TestMain:
    """main() is what the git hook calls with the path of the commit-message file."""

    def test_returns_0_for_a_valid_message(self, tmp_path: Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("JAR-2: add hooks\n", encoding="utf-8")
        assert main([str(msg_file)]) == 0

    def test_returns_1_and_explains_for_an_invalid_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("add hooks\n", encoding="utf-8")
        assert main([str(msg_file)]) == 1
        assert "JAR-<number>: <description>" in capsys.readouterr().err

    def test_returns_2_when_called_without_a_file(self) -> None:
        assert main([]) == 2
