"""Merge a release tag and enforce the fork's single functional change. No compilation."""
import os
import pathlib
import re
import subprocess


def git(*args, check=True):
    return subprocess.run(
        ["git", *args], check=check, text=True, capture_output=True
    ).stdout.strip()


tag = os.environ["UPSTREAM_TAG"]
git("check-ref-format", "refs/tags/" + tag)
git("config", "user.name", "github-actions[bot]")
git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
git("fetch", "--no-tags", "https://github.com/Meloong-Git/PCL.git",
    "refs/tags/" + tag)
upstream_sha = git("rev-parse", "FETCH_HEAD^{commit}")
git("merge", "--no-commit", "--no-ff", upstream_sha)

path = pathlib.Path("Plain Craft Launcher 2/Modules/ModSecret.vb")
original = path.read_bytes()
patched, count = re.subn(
    rb"(Public Const RestrictMcDownload As Boolean = )(?:True|False)\b",
    rb"\g<1>False", original,
)
if count != 1:
    raise RuntimeError("Upstream changed RestrictMcDownload; refusing to publish an unverified build.")
path.write_bytes(patched)

# No unexpected source divergence is allowed to enter a release.
allowed = {
    str(path).replace("\\", "/"),
    "FORK.md",
    ".github/workflows/fork-release.yml",
    ".github/scripts/fork-releases.cjs",
    ".github/scripts/fork-sync.py",
    ".github/scripts/fork-package.ps1",
}
changed = set(git("diff", "--name-only", upstream_sha).splitlines())
if changed - allowed:
    raise RuntimeError(f"Unexpected differences from upstream: {sorted(changed - allowed)}")
upstream_source = subprocess.run(
    ["git", "show", upstream_sha + ":" + str(path).replace("\\", "/")],
    check=True, capture_output=True,
).stdout
expected, count = re.subn(
    rb"(Public Const RestrictMcDownload As Boolean = )(?:True|False)\b",
    rb"\g<1>False", upstream_source,
)
if count != 1 or path.read_bytes().replace(b"\r\n", b"\n") != expected.replace(b"\r\n", b"\n"):
    raise RuntimeError("ModSecret.vb differs from upstream beyond the requested constant.")
git("add", "--", str(path))
if git("status", "--porcelain") or pathlib.Path(".git/MERGE_HEAD").exists():
    git("commit", "-m", f"Follow upstream {tag}; keep Minecraft downloads enabled")
git("push", "origin", "HEAD:main")
git("submodule", "sync", "--recursive")
git("submodule", "update", "--init", "--recursive")
with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
    output.write(f"upstream_sha={upstream_sha}\n")
    output.write(f"source_sha={git('rev-parse', 'HEAD')}\n")
