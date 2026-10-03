# Repository and packaging decisions

The existing single-package `src/` structure is retained. Tests, documentation, scripts and demo
assets have distinct locations; generated distributions, environments and private databases are ignored.
The former unanchored `netops/` pattern also hid application source, so it now targets only the root output folder.
Historical specifications are explicitly archived in place to preserve links and existing tooling paths.

[GitHub recommends a README](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories)
to explain a repository. This project uses a concise README, a focused CI workflow and release notes;
extra badges, contribution bureaucracy and new frameworks are not requirements for a portfolio repository.

[PyPA's packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
explains declared build dependencies and package metadata. This project keeps setuptools and `pyproject.toml`,
declares its GUI dependency and entry point, packages HTML/CSS/JavaScript assets, and verifies the installed wheel.
The chosen Windows dependency pins and source-commit manifest are reproducibility practices for this project,
not universal Python packaging requirements. The build procedure is repeatable; byte-identical output is not asserted.

No project license was found or silently selected. License choice and a distribution-notice review remain
owner decisions. Repository history is preserved; see [publication contents](publication.md).
