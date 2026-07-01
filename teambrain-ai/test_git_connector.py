"""Quick integration test for POST /git/connect."""

import json
import os
import subprocess
import tempfile

import httpx

BASE_URL = "http://127.0.0.1:8000"


def create_test_repo() -> str:
    """Create a temporary Git repo with 3 sample commits."""
    tmpdir = tempfile.mkdtemp(prefix="teambrain_test_")

    run = lambda args: subprocess.run(
        args, cwd=tmpdir, check=True, capture_output=True
    )

    run(["git", "init"])
    run(["git", "config", "user.name", "Jeevan"])
    run(["git", "config", "user.email", "jeevan@teambrain.ai"])

    # Commit 1
    with open(os.path.join(tmpdir, "app.py"), "w") as f:
        f.write("print('hello')\n")
    run(["git", "add", "."])
    run(["git", "commit", "-m", "Initial commit: Flask app skeleton"])

    # Commit 2
    with open(os.path.join(tmpdir, "auth.py"), "w") as f:
        f.write("# JWT auth module\n")
    run(["git", "add", "."])
    run(["git", "commit", "-m", "Implemented JWT Authentication"])

    # Commit 3
    with open(os.path.join(tmpdir, "README.md"), "w") as f:
        f.write("# My Project\n")
    run(["git", "add", "."])
    run(["git", "commit", "-m", "Added README documentation"])

    return tmpdir


def main() -> None:
    repo_path = create_test_repo()
    print(f"Test repo created at: {repo_path}\n")

    # --- Test 1: Valid repo ---
    print("=== TEST 1: POST /git/connect (valid repo) ===")
    r = httpx.post(
        f"{BASE_URL}/git/connect",
        json={"repo_path": repo_path},
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

    # --- Test 2: Invalid path ---
    print("\n=== TEST 2: POST /git/connect (invalid path) ===")
    r = httpx.post(
        f"{BASE_URL}/git/connect",
        json={"repo_path": "C:/nonexistent/fake"},
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

    # --- Test 3: Not a git repo ---
    print("\n=== TEST 3: POST /git/connect (not a git repo) ===")
    not_git = tempfile.mkdtemp(prefix="notgit_")
    r = httpx.post(
        f"{BASE_URL}/git/connect",
        json={"repo_path": not_git},
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

    # --- Test 4: Search for imported commits ---
    print("\n=== TEST 4: GET /memory/search?q=JWT ===")
    r = httpx.get(f"{BASE_URL}/memory/search", params={"q": "JWT"}, timeout=10)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Results: {len(data)}")
    for mem in data:
        print(f"  - {mem['title']}  (author: {mem['author']})")


if __name__ == "__main__":
    main()
