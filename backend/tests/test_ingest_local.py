from fastapi.testclient import TestClient
import main  # Import the module to allow monkeypatching
from pathlib import Path

client = TestClient(main.app)

def test_ingest_local(tmp_path, monkeypatch):
    """
    Tests the /ingest endpoint with a local directory.
    Uses monkeypatch to ensure that the main app writes its data (workspace, index)
    to a temporary directory specific to this test run, preventing state leakage.
    """
    # Create temporary directories for data and workspace inside the test's tmp_path
    test_data_dir = tmp_path / "data"
    test_workspace_dir = test_data_dir / "workspace"
    test_data_dir.mkdir()

    # Use monkeypatch to replace the application's global path variables
    monkeypatch.setattr(main, 'DATA', test_data_dir)
    monkeypatch.setattr(main, 'WORKSPACE', test_workspace_dir)
    monkeypatch.setattr(main, 'INDEX_FILE', test_data_dir / "vectors.faiss")
    monkeypatch.setattr(main, 'META_FILE', test_data_dir / "metadata.json")

    # Set up a toy code repository
    repo = tmp_path / "toy"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "a.py").write_text("""
class Auth:
    def login(self):
        return True
""".strip())
    (repo / "main.py").write_text("""
from pkg.a import Auth

def run():
    return Auth().login()
""".strip())

    # Call the endpoint
    res = client.post("/ingest", data={"github_url": str(repo)})
    
    # Assertions
    assert res.status_code == 200
    js = res.json()
    assert js["status"] == "ingestion complete"
    assert js["chunks"] > 0
    assert (test_data_dir / "vectors.faiss").exists() # Verify index was created
