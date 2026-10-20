# Build, release and rollback

Author: Jason Stys. Portable applications open a local browser UI and run only a fictional normalized thermal analogy. They are unsigned and not intended for real reactor use.

`python tools/package_app.py` freezes the existing production web build, C++ worker and SQL resources into an OS/architecture-specific directory. It runs the **actual frozen executable** for numerical export, health, built HTML and scenario API checks before zipping the entire directory and writing SHA-256. Local builds require the documented C++/Python/Node toolchain; downloaded bundles do not.

The manual **Portable release** workflow creates a draft only when the exact current commit has successful Validation and CodeQL runs. Three platform jobs rebuild and smoke-test native bundles. ZIPs/checksums upload directly to that draft, never Actions artifact storage. A maintainer verifies all jobs, downloads the ZIP/checksum pairs and confirms their hashes before publishing. No automatic unsigned installer, privileged service, cloud deployment or platform store submission occurs.

Verification examples: Windows `Get-FileHash -Algorithm SHA256 <zip>`; Linux `sha256sum -c <checksum>`; macOS `shasum -a 256 -c <checksum>`. Match the entire filename and digest from the same release. Checksums detect accidental corruption, not a compromised publisher. Retain the whole extracted folder. Do not disable OS protections or bypass warnings; prefer reviewed source if blocked.

Platform support is determined by actual CI runner architecture and PyInstaller output, recorded in each asset name. macOS arm64 is not an Intel universal binary. Linux builds inherit the CI image's libc baseline, not compatibility with every older distribution. No native iOS/Android build is supplied. The responsive UI works in supported desktop/mobile browsers when a local runtime is available on that device; it is not remotely exposed by default.

Rollback: close the owned console/app, extract a previous verified release into a new directory and launch it. There is no system installation, auto-update or background service to remove. Optional history files remain user-owned, should be backed up and are not automatically migrated/deleted. Never delete unrelated Actions runs, artifacts or caches as part of this workflow.
