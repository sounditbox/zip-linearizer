"""Тесты для GitHub обработчика."""

from unittest.mock import MagicMock, patch

import pytest

from zip_linearizer.core.exceptions import ProcessingError
from zip_linearizer.core.github_handler import GitHubRepositoryHandler


class TestGitHubRepositoryHandler:
    """Тесты для GitHubRepositoryHandler."""

    def test_parse_repository_url_basic(self):
        """Тест парсинга базового URL репозитория."""
        handler = GitHubRepositoryHandler()
        owner, repo, branch, pr_number = handler.parse_repository_url("https://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"
        assert branch is None
        assert pr_number is None

    def test_parse_repository_url_with_branch(self):
        """Тест парсинга URL с указанием ветки."""
        handler = GitHubRepositoryHandler()
        owner, repo, branch, pr_number = handler.parse_repository_url(
            "https://github.com/owner/repo/tree/main"
        )
        assert owner == "owner"
        assert repo == "repo"
        assert branch == "main"
        assert pr_number is None

    def test_parse_repository_url_with_git_extension(self):
        """Тест парсинга URL с .git расширением."""
        handler = GitHubRepositoryHandler()
        owner, repo, branch, pr_number = handler.parse_repository_url("https://github.com/owner/repo.git")
        assert owner == "owner"
        assert repo == "repo"
        assert branch is None
        assert pr_number is None

    def test_parse_repository_url_with_trailing_slash(self):
        """Тест парсинга URL с завершающим слэшем."""
        handler = GitHubRepositoryHandler()
        owner, repo, branch, pr_number = handler.parse_repository_url("https://github.com/owner/repo/")
        assert owner == "owner"
        assert repo == "repo"
        assert branch is None
        assert pr_number is None

    def test_parse_repository_url_invalid(self):
        """Тест парсинга невалидного URL."""
        handler = GitHubRepositoryHandler()
        with pytest.raises(ProcessingError):
            handler.parse_repository_url("https://gitlab.com/owner/repo")

    def test_parse_repository_url_pull_request(self):
        """Тест парсинга URL Pull Request."""
        handler = GitHubRepositoryHandler()
        owner, repo, branch, pr_number = handler.parse_repository_url(
            "https://github.com/owner/repo/pull/123"
        )
        assert owner == "owner"
        assert repo == "repo"
        assert branch is None
        assert pr_number == 123

    def test_parse_repository_url_pull_request_with_files(self):
        """Тест парсинга URL Pull Request с /files."""
        handler = GitHubRepositoryHandler()
        owner, repo, branch, pr_number = handler.parse_repository_url(
            "https://github.com/owner/repo/pull/123/files"
        )
        assert owner == "owner"
        assert repo == "repo"
        assert branch is None
        assert pr_number == 123

    def test_parse_repository_url_pull_request_without_number(self):
        """Тест парсинга URL PR без номера."""
        handler = GitHubRepositoryHandler()
        with pytest.raises(ProcessingError):
            handler.parse_repository_url("https://github.com/owner/repo/pull")

    def test_parse_repository_url_pull_request_with_trailing_slash(self):
        """Тест парсинга URL PR с завершающим слэшем."""
        handler = GitHubRepositoryHandler()
        owner, repo, branch, pr_number = handler.parse_repository_url(
            "https://github.com/owner/repo/pull/123/"
        )
        assert owner == "owner"
        assert repo == "repo"
        assert pr_number == 123

    @patch("zip_linearizer.core.github_handler.requests.Session")
    def test_get_default_branch(self, mock_session_class):
        """Тест получения дефолтной ветки."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {"default_branch": "main"}
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        handler = GitHubRepositoryHandler()
        branch = handler.get_default_branch("owner", "repo")
        assert branch == "main"

    @patch("zip_linearizer.core.github_handler.requests.Session")
    def test_get_default_branch_fallback(self, mock_session_class):
        """Тест fallback на 'main' если дефолтная ветка не указана."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        handler = GitHubRepositoryHandler()
        branch = handler.get_default_branch("owner", "repo")
        assert branch == "main"

    @patch("zip_linearizer.core.github_handler.requests.Session")
    def test_get_default_branch_error(self, mock_session_class):
        """Тест обработки ошибки при получении дефолтной ветки."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        import requests

        mock_session.get.side_effect = requests.RequestException("Connection error")

        handler = GitHubRepositoryHandler()
        with pytest.raises(ProcessingError):
            handler.get_default_branch("owner", "repo")

    @patch("zip_linearizer.core.github_handler.tempfile.gettempdir")
    @patch("zip_linearizer.core.github_handler.requests.Session")
    def test_download_repository(self, mock_session_class, mock_gettempdir):
        """Тест скачивания репозитория."""
        mock_gettempdir.return_value = "/tmp"

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"zip", b"content"]
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        handler = GitHubRepositoryHandler()

        with patch("zip_linearizer.core.github_handler.Path") as mock_path:
            mock_file = MagicMock()
            mock_path.return_value.__truediv__ = MagicMock(return_value=mock_file)
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=False)
            mock_file.write = MagicMock()

            with patch("builtins.open", create=True):
                zip_path = handler.download_repository("owner", "repo", "main")
                assert zip_path is not None

    def test_cleanup_temp_file(self):
        """Тест очистки временного файла."""
        handler = GitHubRepositoryHandler()

        with patch("zip_linearizer.core.github_handler.Path") as mock_path:
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            mock_path.return_value = mock_file

            handler.cleanup_temp_file(mock_file)
            mock_file.unlink.assert_called_once()

    def test_parse_repository_url_short_format(self):
        """Тест парсинга короткого формата URL."""
        handler = GitHubRepositoryHandler()
        with pytest.raises(ProcessingError):
            handler.parse_repository_url("https://github.com/owner")

    @patch("zip_linearizer.core.github_handler.requests.Session")
    def test_get_pull_request_info(self, mock_session_class):
        """Тест получения информации о Pull Request."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "head": {
                "ref": "feature-branch",
                "repo": {
                    "owner": {"login": "feature-owner"},
                    "name": "feature-repo",
                    "full_name": "feature-owner/feature-repo",
                },
            },
            "base": {"ref": "main"},
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        handler = GitHubRepositoryHandler()
        pr_info = handler.get_pull_request_info("owner", "repo", 123)

        assert pr_info["head_branch"] == "feature-branch"
        assert pr_info["head_owner"] == "feature-owner"
        assert pr_info["head_repo"] == "feature-repo"
        assert pr_info["base_branch"] == "main"

    @patch("zip_linearizer.core.github_handler.requests.Session")
    def test_get_pull_request_info_with_fork(self, mock_session_class):
        """Тест получения информации о PR из форка репозитория."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "head": {
                "ref": "feature-branch",
                "repo": {
                    "owner": {"login": "fork-owner"},
                    "name": "original-repo",
                    "full_name": "fork-owner/original-repo",
                },
            },
            "base": {"ref": "main"},
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        handler = GitHubRepositoryHandler()
        pr_info = handler.get_pull_request_info("original-owner", "original-repo", 123)

        assert pr_info["head_branch"] == "feature-branch"
        assert pr_info["head_owner"] == "fork-owner"
        assert pr_info["head_repo"] == "original-repo"
        assert pr_info["base_branch"] == "main"

    @patch("zip_linearizer.core.github_handler.requests.Session")
    def test_get_pull_request_info_missing_head_branch(self, mock_session_class):
        """Тест обработки PR без head branch."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "head": {},
            "base": {"ref": "main"},
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        handler = GitHubRepositoryHandler()
        with pytest.raises(ProcessingError) as exc_info:
            handler.get_pull_request_info("owner", "repo", 123)
        assert "Не удалось определить ветку" in str(exc_info.value)

    @patch("zip_linearizer.core.github_handler.requests.Session")
    def test_get_pull_request_info_missing_head_repo(self, mock_session_class):
        """Тест обработки PR без head repo."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "head": {
                "ref": "feature-branch",
                "repo": None,
            },
            "base": {"ref": "main"},
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        handler = GitHubRepositoryHandler()
        pr_info = handler.get_pull_request_info("owner", "repo", 123)

        # Должен использовать исходные owner и repo если head.repo отсутствует
        assert pr_info["head_branch"] == "feature-branch"
        assert pr_info["head_owner"] == "owner"
        assert pr_info["head_repo"] == "repo"

    @patch("zip_linearizer.core.github_handler.requests.Session")
    def test_get_pull_request_info_error(self, mock_session_class):
        """Тест обработки ошибки при получении информации о PR."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        import requests

        mock_session.get.side_effect = requests.RequestException("PR not found")

        handler = GitHubRepositoryHandler()
        with pytest.raises(ProcessingError):
            handler.get_pull_request_info("owner", "repo", 999)

    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler.get_pull_request_info")
    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler.download_repository")
    def test_download_from_url_pull_request_from_fork(
        self, mock_download, mock_get_pr_info
    ):
        """Тест скачивания архива из PR форка репозитория."""
        mock_get_pr_info.return_value = {
            "head_branch": "feature-branch",
            "head_owner": "fork-owner",
            "head_repo": "repo",
            "base_branch": "main",
        }

        mock_zip_path = MagicMock()
        mock_download.return_value = mock_zip_path

        handler = GitHubRepositoryHandler()
        result = handler.download_from_url("https://github.com/original-owner/repo/pull/123")

        mock_get_pr_info.assert_called_once_with("original-owner", "repo", 123)
        # Должен использовать head_owner и head_repo из PR
        mock_download.assert_called_once_with("fork-owner", "repo", "feature-branch")
        assert result == mock_zip_path

    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler.get_pull_request_info")
    def test_download_from_url_pull_request_error(self, mock_get_pr_info):
        """Тест обработки ошибки при получении информации о PR."""
        mock_get_pr_info.side_effect = ProcessingError("PR not found")

        handler = GitHubRepositoryHandler()
        with pytest.raises(ProcessingError):
            handler.download_from_url("https://github.com/owner/repo/pull/999")

    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler.get_pull_request_info")
    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler.download_repository")
    def test_download_from_url_regular_repo(self, mock_download, mock_get_pr_info):
        """Тест скачивания обычного репозитория (не PR)."""
        mock_zip_path = MagicMock()
        mock_download.return_value = mock_zip_path

        handler = GitHubRepositoryHandler()
        result = handler.download_from_url("https://github.com/owner/repo")

        # Для обычного репозитория get_pull_request_info не должен вызываться
        mock_get_pr_info.assert_not_called()
        mock_download.assert_called_once_with("owner", "repo", None)
        assert result == mock_zip_path

