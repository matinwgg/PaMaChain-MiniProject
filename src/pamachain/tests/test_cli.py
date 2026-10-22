import pytest

from pamachain import cli


@pytest.fixture
def cli_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PAMACHAIN_LEDGER", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("PAMACHAIN_LEDGER_KEY", str(tmp_path / "key.pem"))
    monkeypatch.setenv("PAMACHAIN_LEDGER_ANCHOR", str(tmp_path / "head.json"))
    monkeypatch.setenv("PAMACHAIN_KEYSTORE", str(tmp_path / "keystore.json"))
    return tmp_path


def test_init_add_and_view(cli_env, monkeypatch, capsys):
    prompts = iter(
        [
            "correct horse battery",
            "correct horse battery",
            "correct horse battery",
            "correct horse battery",
        ]
    )
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt="": next(prompts))

    cli.init()
    cli.add("github", "s3cret")
    cli.view()

    output = capsys.readouterr().out
    assert "Vault initialised." in output
    assert "github: s3cret" in output


def test_wrong_password_blocks_access(cli_env, monkeypatch):
    prompts = iter(["correct horse battery", "correct horse battery"])
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt="": next(prompts))
    cli.init()

    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt="": "wrong password")
    with pytest.raises(SystemExit, match="Incorrect master password"):
        cli.add("github", "s3cret")


def test_init_refuses_to_overwrite(cli_env, monkeypatch):
    prompts = iter(["correct horse battery", "correct horse battery"])
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt="": next(prompts))
    cli.init()

    with pytest.raises(SystemExit, match="already initialised"):
        cli.init()
