# lacodda scoop bucket

Scoop manifests for the programs of the lacodda line.

```powershell
scoop bucket add lacodda https://github.com/lacodda/scoop-bucket
scoop install turnout
```

| Manifest | What it is |
| --- | --- |
| [`turnout`](https://github.com/lacodda/turnout) | A developer's switchyard: point local apps at any backend stand, keep servers and secrets at hand, build and deploy from any directory. Installs `turnout` and the alias `tn`. |

Each manifest installs the release's own Windows x86-64 archive, checked against the SHA-256 written in it.

## How the manifests are kept

Nothing in `bucket/` is written by hand. `tools/update.py` reads `packages.json` and each package's newest GitHub release, hashes the archive and writes the manifest, with Scoop's own `checkver` and `autoupdate` for Scoop's tools; the `Update` workflow runs it every four hours and on demand, commits what changed and installs every manifest on Windows to prove it. A new program joins the bucket as one entry in `packages.json`.

## License

MIT (c) [Kirill Lakhtachev](https://lacodda.com)
