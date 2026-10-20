# Security and privacy

By Jason Stys. This educational local application has no accounts, sensitive data ingestion, hardware, remote model or network-fetch integration. Do not put plant data, credentials or personal records into modified builds or issue reports.

Trust boundary: the reviewed executable and local OS are trusted; browser requests are not. Host/origin/Fetch-Site checks reduce DNS-rebinding and cross-origin access. Assets are allowlisted and resolved under a dedicated build directory, including symlink confinement. HTTP never exposes source or arbitrary filesystem paths. Restrictive CSP, frame denial, nosniff, no-referrer and permissions policy apply to successes and failures. There are no ads, third-party scripts, analytics or external fonts to block.

Inputs are finite reviewed settings; the native parser also validates numeric tokens and ranges. The subprocess has a fixed owned executable path, no shell and a timeout. Worker output is checked for bounded size, schema, grid, finite values, nonnegative thermal states and ledger consistency before display. Output validation is not a sandbox for a malicious replacement executable. Protect the extracted bundle against local modification.

History uses parameterized SQL, content hashes, immutable triggers and a 100-run cap; it is local CLI opt-in, not an authentication system. Browser settings contain no personal information. Exports intentionally remain on the user's device. Normal OS file permissions apply; there is no claim of encryption or protection from an administrator/malware on the same machine.

The standard-library threaded server is **not hardened public hosting**. It binds only `127.0.0.1`; do not proxy it to the Internet or change that boundary without a separate production design. A local hostile process can still consume resources; the bounded model, 10-second worker timeout and LRU do not provide a global request-rate guarantee. Large malformed HTTP headers and platform behavior retain the standard-library server's limitations.

Supply chain: hash-locked Python development packages, npm integrity lock, pinned Action commits, read-only default workflow permissions, CodeQL for C++/Python/TypeScript, native ASan/UBSan, dependency audits. No embedded tokens, credentials or secret settings. Actions caches and artifacts are disabled; release assets are separate. No automated scan proves absence of vulnerabilities. Bundles are unsigned, not notarized and not guaranteed accepted by endpoint protection; never disable security protections to launch them.

Report a reproducible issue through the [repository](https://github.com/JasonStys/reactor-systems-simulator/issues) or contact [Jason Stys](https://github.com/JasonStys). Do not attach secrets or sensitive data. This software must never be used for reactor design, operations, radiation/dose assessment or nuclear safety decisions.
