from typing import Any

import requests


class Session:
    """
    Session class that authenticates and stores tokens for requests to the API
    """

    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token_auth = {}
        self.token_download = ""
        self.group = ""

        self._login(email, password)

    def _login(self, email: str, password: str):
        """
        Authenticates and stores session token and file download token.
        """
        resp = self.session.post(
            f"{self.base_url}/api/login", json={"email": email, "password": password}
        )
        resp.raise_for_status()
        data = resp.json()

        token = data.get("token")
        files_token = data.get("filesToken")

        self.token_auth = {"authorization": f"bearer {token}"}
        self.token_download = f"=&auth={files_token}"

        user_info = self.api_get("currentUser")
        self.group = user_info.get("group")

    def api_get(self, path: str) -> dict[str, Any]:
        """
        Performs an authenticated GET request to the API and returns the JSON response.
        """
        resp = self.session.get(f"{self.base_url}/api/{path}", headers=self.token_auth)
        resp.raise_for_status()
        return resp.json()

    def download_file(self, file_url: str, file_path: str):
        """
        Downloads a single file with the download token.
        """
        if not file_url.lower().startswith("/api/file"):
            return

        with open(file_path, "wb") as f:
            resp = self.session.get(f"{self.base_url}{file_url}{self.token_download}")
            f.write(resp.content)

    def submit_flag(self, challenge_id: int, flag: str) -> dict[str, Any]:
        """
        Submits a flag for a specific challenge.
        """
        payload = {"flag": flag}
        resp = self.session.post(
            f"{self.base_url}/api/challenges/{challenge_id}/flag",
            json=payload,
            headers=self.token_auth,
        )
        return resp.json()

    def get_solved_ids(self) -> list[int]:
        """
        Fetches the list of solved challenge IDs from the API.
        Endpoint: /api/player/unlocks
        """
        try:
            data = self.api_get("player/unlocks")
            solved_ids = data.get("solves", [])
            return solved_ids
        except Exception as e:
            print(f"\n\033[91m[!] Error fetching solved IDs: {e}\033[0m")
        return []
