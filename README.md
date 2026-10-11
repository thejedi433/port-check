# port-check

A minimal CLI tool to check if a port is open on a host.

## Installation

```bash
uv venv
uv pip install -e .
```

## Usage

```bash
port-check <host> <port> [timeout]
```

### Examples

```bash
# Check if port 80 is open on localhost
port-check localhost 80

# Check a remote host with custom timeout
port-check example.com 443 5.0
```

## Exit Codes

- `0` - Port is open
- `1` - Port is closed or error occurred
