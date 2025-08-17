from fastapi.testclient import TestClient
import main # Import the module to allow monkeypatching

client = TestClient(main.app)

def test_roundtrip(tmp_path, monkeypatch):
    """
    Tests a full ingest-then-query cycle.
    Uses monkeypatch to isolate the data and index files to a temporary directory,
    ensuring this test does not interfere with any other tests.
    """
    # Create and assign temporary paths for this test
    test_data_dir = tmp_path / "data"
    test_workspace_dir = test_data_dir / "workspace"
    test_data_dir.mkdir()
    
    monkeypatch.setattr(main, 'DATA', test_data_dir)
    monkeypatch.setattr(main, 'WORKSPACE', test_workspace_dir)
    monkeypatch.setattr(main, 'INDEX_FILE', test_data_dir / "vectors.faiss")
    monkeypatch.setattr(main, 'META_FILE', test_data_dir / "metadata.json")

    # 1. Create a toy repository
    repo = tmp_path / "toy"
    repo.mkdir()
    (repo / "main.py").write_text("""
class Greeter:
    def hello(self, name: str):
        # This is where the greeting happens
        return f"hi {name}"
""".strip())

    # 2. Ingest the repository
    r = client.post("/ingest", data={"github_url": str(repo)})
    assert r.status_code == 200
    assert (test_data_dir / "vectors.faiss").exists()

    # 3. Query the ingested code
    q = client.post("/query", data={"query": "where is greeting done?", "k": 3})
    assert q.status_code == 200
    
    data = q.json()
    assert "answer" in data
    assert "matches" in data
    assert len(data["matches"]) > 0
    # Check that the match is from the correct file
    assert data["matches"][0]["file"] == "main.py"
