"""Module for working with GitHub repositories."""

import re
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

from zip_linearizer.core.exceptions import ProcessingError
from zip_linearizer.utils.logger import get_logger


class GitHubRepositoryHandler:
    """Handler for working with GitHub repositories."""

    GITHUB_API_BASE = "https://api.github.com"
    GITHUB_ARCHIVE_URL_TEMPLATE = (
        "https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    )

    def __init__(self, timeout: int = 30):
        """
        Initialize GitHub repository handler.

        Args:
            timeout: HTTP request timeout in seconds.
        """
        self._timeout = timeout
        self._logger = get_logger(__name__)
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "Zip-Linearizer/1.0",
                "Accept": "application/vnd.github.v3+json",
            }
        )

    def parse_repository_url(self, url: str) -> tuple[str, str, Optional[str], Optional[int]]:
        """
        Parse GitHub repository or Pull Request URL.

        Args:
            url: Repository URL (e.g., https://github.com/owner/repo)
                 or Pull Request (e.g., https://github.com/owner/repo/pull/123).

        Returns:
            Tuple (owner, repo, branch, pr_number).
            branch and pr_number can be None.

        Raises:
            ProcessingError: If URL is not a valid GitHub URL.
        """
        # Normalize URL
        url = url.strip().rstrip("/")

        # Remove .git suffix if present
        if url.endswith(".git"):
            url = url[:-4]

        # Remove /files suffix for PR
        if url.endswith("/files"):
            url = url[:-6]

        # Parse URL
        parsed = urlparse(url)

        # Check if it's a GitHub URL
        if "github.com" not in parsed.netloc.lower():
            raise ProcessingError(f"URL is not a GitHub repository: {url}")

        # Extract owner and repo from path
        path_parts = [p for p in parsed.path.split("/") if p]

        if len(path_parts) < 2:
            raise ProcessingError(f"Invalid repository URL format: {url}")

        owner = path_parts[0]
        repo = path_parts[1]

        # Check if it's a Pull Request
        pr_number = None
        branch = None

        if len(path_parts) >= 3 and path_parts[2] == "pull":
            # This is a Pull Request
            if len(path_parts) >= 4:
                try:
                    pr_number = int(path_parts[3])
                except ValueError:
                    raise ProcessingError(f"Invalid Pull Request number: {path_parts[3]}")
            else:
                raise ProcessingError(f"Pull Request number not specified in URL: {url}")
        elif len(path_parts) >= 3 and path_parts[2] == "tree":
            # This is a branch link
            branch = path_parts[3] if len(path_parts) > 3 else None
        elif len(path_parts) >= 3 and path_parts[2] == "archive":
            # If it's a direct archive link
            match = re.search(r"/(\w+)\.zip$", url)
            if match:
                branch = match.group(1)

        return owner, repo, branch, pr_number

    def get_pull_request_info(self, owner: str, repo: str, pr_number: int) -> dict:
        """
        Get Pull Request information via GitHub API.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull Request number.

        Returns:
            Dictionary with PR information, including head branch.

        Raises:
            ProcessingError: If failed to get PR information.
        """
        try:
            url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
            self._logger.debug(f"Requesting PR information: {url}")
            response = self._session.get(url, timeout=self._timeout)
            response.raise_for_status()

            data = response.json()
            head_branch = data.get("head", {}).get("ref")
            head_repo = data.get("head", {}).get("repo", {})

            if not head_branch:
                raise ProcessingError(f"Failed to determine branch for PR #{pr_number}")

            self._logger.info(
                f"PR #{pr_number}: source branch = {head_branch}, "
                f"repository = {head_repo.get('full_name', f'{owner}/{repo}')}"
            )

            return {
                "head_branch": head_branch,
                "head_owner": head_repo.get("owner", {}).get("login", owner),
                "head_repo": head_repo.get("name", repo),
                "base_branch": data.get("base", {}).get("ref"),
            }
        except requests.RequestException as e:
            raise ProcessingError(
                f"Failed to get PR #{pr_number} information for repository {owner}/{repo}: {e}"
            ) from e

    def get_default_branch(self, owner: str, repo: str) -> str:
        """
        Get repository default branch via GitHub API.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Default branch name.

        Raises:
            ProcessingError: If failed to get repository information.
        """
        try:
            url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}"
            self._logger.debug(f"Requesting repository information: {url}")
            response = self._session.get(url, timeout=self._timeout)
            response.raise_for_status()

            data = response.json()
            branch = data.get("default_branch", "main")
            self._logger.info(f"Repository default branch: {branch}")
            return branch
        except requests.RequestException as e:
            raise ProcessingError(
                f"Failed to get repository {owner}/{repo} information: {e}"
            ) from e

    def download_repository(self, owner: str, repo: str, branch: Optional[str] = None) -> Path:
        """
        Download GitHub repository archive.

        Args:
            owner: Repository owner.
            repo: Repository name.
            branch: Branch (if None, default branch is used).

        Returns:
            Path to downloaded ZIP file.

        Raises:
            ProcessingError: If failed to download archive.
        """
        # Get default branch if not specified
        if branch is None:
            branch = self.get_default_branch(owner, repo)

        # Build archive download URL
        archive_url = self.GITHUB_ARCHIVE_URL_TEMPLATE.format(
            owner=owner, repo=repo, branch=branch
        )

        self._logger.info(f"Downloading repository archive: {archive_url}")

        try:
            # Download archive
            response = self._session.get(archive_url, timeout=self._timeout, stream=True)
            response.raise_for_status()

            # Create temporary file
            temp_dir = Path(tempfile.gettempdir())
            zip_filename = f"{owner}-{repo}-{branch}.zip"
            zip_path = temp_dir / zip_filename

            # Save archive
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self._logger.info(f"Archive downloaded: {zip_path}")
            return zip_path

        except requests.RequestException as e:
            raise ProcessingError(
                f"Failed to download repository {owner}/{repo} archive: {e}"
            ) from e

    def download_from_url(self, url: str) -> Path:
        """
        Download repository archive by URL.

        Args:
            url: GitHub repository or Pull Request URL.

        Returns:
            Path to downloaded ZIP file.
        """
        owner, repo, branch, pr_number = self.parse_repository_url(url)

        # If it's a Pull Request, get its information
        if pr_number is not None:
            self._logger.info(f"Pull Request #{pr_number} detected")
            pr_info = self.get_pull_request_info(owner, repo, pr_number)
            # Use source branch from PR
            owner = pr_info["head_owner"]
            repo = pr_info["head_repo"]
            branch = pr_info["head_branch"]
            self._logger.info(
                f"Downloading branch '{branch}' from repository {owner}/{repo}"
            )

        return self.download_repository(owner, repo, branch)

    def cleanup_temp_file(self, zip_path: Path) -> None:
        """
        Delete temporary archive file.

        Args:
            zip_path: Path to file to delete.
        """
        try:
            if zip_path.exists():
                zip_path.unlink()
                self._logger.debug(f"Temporary file deleted: {zip_path}")
        except Exception as e:
            self._logger.warning(f"Failed to delete temporary file {zip_path}: {e}")

