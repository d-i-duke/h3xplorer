<!--- the "--8<--" html comments define what part of the README to add to the index page of the documentation -->
<!--- --8<-- [start:docs] -->
![h3xplorer](resources/logos/title.png)

# h3xplorer (h3xplorer)

[![Daily CI Build](https://github.com/d-i-duke/h3xplorer/actions/workflows/daily-scheduled-ci.yml/badge.svg)](https://github.com/d-i-duke/h3xplorer/actions/workflows/daily-scheduled-ci.yml)
[![Documentation](https://github.com/d-i-duke/h3xplorer/actions/workflows/pages/pages-build-deployment/badge.svg?branch=gh-pages)](https://d-i-duke.github.io/h3xplorer)

<!--- --8<-- [end:docs] -->

## Documentation

For more detailed instructions, see our [documentation](https://d-i-duke.github.io/h3xplorer/latest).

## Installation

To install h3xplorer, we recommend using the [conda](https://docs.conda.io/en/latest/) package manager, accessible from the terminal by installing [miniforge](https://github.com/conda-forge/miniforge?tab=readme-ov-file#download).
Arup users on Windows can install `miniforge` from the Arup software shop by downloading "VS Code for Python" and then access `conda` from the VSCode integrated terminal.

### As a user

<!--- --8<-- [start:docs-install-user] -->

``` shell

git clone git@github.com:d-i-duke/h3xplorer.git
cd h3xplorer
conda create -n h3xplorer -c conda-forge --file requirements/base.txt
conda activate h3xplorer
pip install --no-deps -e .
```

<!--- --8<-- [end:docs-install-user] -->

### As a developer

<!--- --8<-- [start:docs-install-dev] -->

``` shell
git clone git@github.com:d-i-duke/h3xplorer.git
cd h3xplorer
conda create -n h3xplorer -c conda-forge --file requirements/base.txt --file requirements/dev.txt
conda activate h3xplorer
pip install --no-deps -e .
```

<!--- --8<-- [end:docs-install-dev] -->

For more detailed instructions, see our [documentation](https://d-i-duke.github.io/h3xplorer/latest/installation/).

## Contributing

There are many ways to contribute to h3xplorer.
Before making contributions to the h3xplorer source code, see our contribution guidelines and follow the [development install instructions](#as-a-developer).

If you plan to make changes to the code then please make regular use of the following tools to verify the codebase while you work:

- `pre-commit`: run `pre-commit install` in your command line to load inbuilt checks that will run every time you commit your changes.
  The checks are: 1. check no large files have been staged, 2. lint python files for major errors, 3. format python files to conform with the [pep8 standard](https://peps.python.org/pep-0008/).
  You can also run these checks yourself at any time to ensure staged changes are clean by simple calling `pre-commit`.
- `pytest` - run the unit test suite and check test coverage.
- `pytest -p memray -m "high_mem" --no-cov` (not available on Windows) - after installing memray (`conda install memray pytest-memray`), test that memory and time performance does not exceed benchmarks.

For more information, see our [documentation](https://d-i-duke.github.io/h3xplorer/latest/contributing/).

## Building the documentation

If you are unable to access the online documentation, you can build the documentation locally.
First, [install a development environment of h3xplorer](https://d-i-duke.github.io/h3xplorer/latest/contributing/coding/), then deploy the documentation using [MkDocs](https://www.mkdocs.org/):

``` shell
mkdocs serve
```

Then you can view the documentation in a browser at <http://localhost:8000/>.

## License

Copyright (c) 2025 h3xplorer developers & contributors listed in AUTHORS.md.
Licensed under the GPL-v3.

## Credits

This package was created with [Copier](https://copier.readthedocs.io/) and the [arup-group/pypackage-template](https://github.com/arup-group/pypackage-template) project template.
