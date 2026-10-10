# Animated GitHub profile

Edit `profile.json`, then run `python3 scripts/build_profile.py` to regenerate the README and SVGs. The daily GitHub Actions workflow refreshes the public contribution calendar at 06:17 UTC (scheduler delays are possible).

The terminal header uses a custom ASCII SK monogram, rather than a photo portrait. Brief animations settle into static readable content; reduced-motion preferences are supported where the SVG renderer honors them. No third-party image service, personal access token, or Python packages are required. GitHub Actions uses its built-in repository token for commits.

Contribution HTML is an undocumented GitHub endpoint. A fetch or parser failure stops the refresh without replacing committed assets. Counts reflect GitHub's public calendar; no private repository details are fetched. Benchmarks are local results, not production service guarantees.

Inspired by [Avi Vashishta's guide](https://www.avivashishta.com/blog/build-animated-github-profile-readme), with an original generator and personal content.
