# widget-cli

Converts widget manifests (v2 JSON) to TOML. Reads from stdin, writes to stdout.

## Install

```bash
npm install -g widget-cli
```

## Usage

Pipe a manifest through the converter and check the exit code. Exit 3 means the
manifest referenced an unknown schema version; run `widget-cli schemas` to list
the versions this build supports, then pin `schema_version` in the manifest.

The `--strict` flag rejects unknown keys instead of passing them through. Use it
in CI. Without it, unknown keys survive the round-trip untouched, which is the
right default for local experimentation.
