# Install your animated profile

Prepared for **SaiSumedh18**. Includes an animated terminal card, real contribution calendar, four featured projects, and daily refresh automation. No Python packages or personal access token are required for the workflow.

1. Create a **public** repository named **SaiSumedh18** under your GitHub account, or open the existing repository of that name.
2. Copy this folder's contents into the repository root, including `.github/workflows/update-profile.yml`. Keep existing repository content you want to preserve. README.md becomes your profile introduction.
3. Commit the files to the default branch. In **Actions → Refresh profile**, choose **Run workflow** if the initial push has not already triggered it.
4. Check that the workflow succeeds and your profile displays both SVGs.

If pushing from a terminal, authenticate first using `gh auth login --hostname github.com`. The local saved login was expired when this package was prepared, so no repository changes have been pushed.

## Editing

Edit `profile.json`, then run:

```sh
python3 scripts/build_profile.py
```

To fetch fresh public contribution data as well:

```sh
python3 scripts/build_profile.py --fetch
```

Project selection is curated from the three most recently pushed public repositories at preparation time, plus the user-provided InsightChat AI link; the daily workflow refreshes contributions, not project selection. Names, project descriptions, and toolbox entries are editable. The stack was drawn from repository descriptions rather than unverified employment or certification claims.

## Design and operation

The SVGs use a brief entrance animation that settles into a readable final state, with reduced-motion support where the renderer honors it. All images are committed locally. The illustration represents build, ship, and operate; it can be replaced with a portrait later if desired.

The daily schedule is 06:17 UTC, subject to GitHub's scheduler delays. The workflow uses the repository's built-in token with contents write permission. A branch protection policy that blocks bot pushes may require a pull-request-based update flow. Fetch or parser failures stop the job and preserve committed assets. Public contribution HTML is an undocumented interface and may require parser maintenance if GitHub changes its markup. No private repository details are fetched.

Source inspiration: https://www.avivashishta.com/blog/build-animated-github-profile-readme

InsightChat AI is publicly accessible. Its description, portfolio link, and LinkedIn link were checked against its public repository README.
