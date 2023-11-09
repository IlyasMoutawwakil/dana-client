# Dana Client

A 
Dana Client is a Python HTTP client to interact with a [Dana Server](https://github.com/IlyasMoutawwakil/dana-server) and publish benchmarks to it.

## Installation

```bash
pip install -e .
```

# Usage

`dana_client.api` contains the basic functionalities of the client like login, adding a project, series, etc.
`dana_client.build_utils` contains functions for publishing and uploading a benchmarks.

## Commands

It also comes with two commands that we use for benchmarking purposes : `publish-backup`, `update-project`.
