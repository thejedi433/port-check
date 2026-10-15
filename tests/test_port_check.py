"""Tests for port-check."""

import socket
import sys
import threading
import pytest
from port_check import check_port, main


def test_check_port_open():
    """Test that check_port returns True for an open port."""
    # Start a simple TCP server on a random port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    
    def accept():
        conn, _ = server.accept()
        conn.close()
    
    t = threading.Thread(target=accept, daemon=True)
    t.start()
    
    try:
        assert check_port("127.0.0.1", port, timeout=2.0) is True
    finally:
        server.close()
        t.join(timeout=2)


def test_check_port_closed():
    """Test that check_port returns False for a closed port."""
    # Use a port that's very unlikely to be open
    assert check_port("127.0.0.1", 59999, timeout=0.5) is False


def test_check_port_invalid_host():
    """Test that check_port handles invalid host gracefully."""
    assert check_port("invalid.host.that.does.not.exist.example", 80, timeout=1.0) is False


def test_main_success(capsys):
    """Test main with valid open port."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    
    def accept():
        conn, _ = server.accept()
        conn.close()
    
    t = threading.Thread(target=accept, daemon=True)
    t.start()
    
    old_argv = sys.argv
    sys.argv = ["port-check", "127.0.0.1", str(port)]
    try:
        result = main()
        assert result == 0
    finally:
        sys.argv = old_argv
        server.close()
        t.join(timeout=2)
    
    captured = capsys.readouterr()
    assert "open" in captured.out


def test_main_failure(capsys):
    """Test main with closed port."""
    old_argv = sys.argv
    sys.argv = ["port-check", "127.0.0.1", "59999"]
    try:
        result = main()
        assert result == 1
    finally:
        sys.argv = old_argv
    
    captured = capsys.readouterr()
    assert "closed" in captured.out


def test_main_invalid_port(capsys):
    """Test main with invalid port number."""
    old_argv = sys.argv
    sys.argv = ["port-check", "localhost", "99999"]
    try:
        result = main()
        assert result == 1
    finally:
        sys.argv = old_argv
    
    captured = capsys.readouterr()
    assert "Error" in captured.out or "Invalid" in captured.out


def test_main_too_few_args(capsys):
    """Test main with insufficient arguments."""
    old_argv = sys.argv
    sys.argv = ["port-check"]
    try:
        result = main()
        assert result == 1
    finally:
        sys.argv = old_argv
    
    captured = capsys.readouterr()
    assert "Usage" in captured.out


def test_main_custom_timeout(capsys):
    """Test main with custom timeout."""
    old_argv = sys.argv
    sys.argv = ["port-check", "127.0.0.1", "59999", "0.1"]
    try:
        result = main()
        assert result == 1
    finally:
        sys.argv = old_argv


def test_main_invalid_timeout(capsys):
    """Test main with invalid timeout."""
    old_argv = sys.argv
    sys.argv = ["port-check", "localhost", "80", "notanumber"]
    try:
        result = main()
        assert result == 1
    finally:
        sys.argv = old_argv
    
    captured = capsys.readouterr()
    assert "Invalid timeout" in captured.out


def test_main_module_invocation(capsys):
    """Test that __main__.py works when invoked as module."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "port_check", "127.0.0.1", "59999"],
        capture_output=True,
        text=True,
        timeout=5
    )
    assert result.returncode == 1
    assert "closed" in result.stdout


def test_main_module_direct_execution(monkeypatch):
    """Test __main__.py execution path via runpy (covers the __name__ guard)."""
    import runpy
    old_argv = sys.argv
    sys.argv = ["port-check", "127.0.0.1", "59999"]
    try:
        # runpy executes the module's top-level code including the
        # `if __name__ == "__main__": sys.exit(main())` block. A closed port
        # causes main() to return 1, which propagates as SystemExit.
        with pytest.raises(SystemExit) as exc:
            runpy.run_module("port_check.__main__", run_name="__main__")
        assert exc.value.code == 1
    finally:
        sys.argv = old_argv
