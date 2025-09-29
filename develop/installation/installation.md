
# Installation

## Installing a user environment

As a `h3xplorer` user, it is easiest to install using the [conda](https://docs.conda.io/en/latest/) package manager, as follows:

1. Install conda with the [miniforge](https://github.com/conda-forge/miniforge?tab=readme-ov-file#download) executable for your operating system.
   Arup users on Windows can install `miniforge` from the Arup software shop by downloading "VS Code for Python".
1. Open the command line (or the VSCode "integrated terminal" in Windows).
1. Download (a.k.a., clone) the h3xplorer repository: `git clone git@github.com:d-i-duke/h3xplorer.git`
1. Change into the `h3xplorer` directory: `cd h3xplorer`
1. Create the h3xplorer conda environment: `conda create -n h3xplorer -c conda-forge --file requirements/base.txt`
1. Activate the h3xplorer conda environment: `conda activate h3xplorer`
1. Install the h3xplorer package into the environment, ignoring dependencies (we have dealt with those when creating the conda environment): `pip install --no-deps .`

All together:

--8<-- "README.md:docs-install-user"

!!! tip
    If you are an Arup user and are having difficulties with creating the `conda` environment, it may be due to *SSL certificates*.
    You'll know that this is the case because there will be mention of "SSL" in the error trace.
    Search `SSL Certificates` on the Arup internal Sharepoint to find instructions on adding the certificates for `conda`.
    Windows users who have installed "VS Code for Python" from the software shop should have all the relevant certificates in place, but you will need to follow the instructions given on the SharePoint troubleshooting page if you want to run the command from in a Windows Subsystem for Linux (WSL) session.

### Running the example notebooks

If you have followed the non-developer installation instructions above, you will need to install `jupyter` into your `h3xplorer` environment to run the [example notebooks](https://github.com/d-i-duke/h3xplorer/tree/main/examples):

``` shell
conda install -n h3xplorer jupyter
```

With Jupyter installed, it's easiest to then add the environment as a jupyter kernel:

``` shell
conda activate h3xplorer
ipython kernel install --user --name=h3xplorer
jupyter notebook
```

### Choosing a different environment name

If you would like to use a different name to `h3xplorer` for your conda environment, the installation becomes (where `[my-env-name]` is your preferred name for the environment):

``` shell
conda create -n [my-env-name] -c conda-forge --file requirements/base.txt
conda activate [my-env-name]
ipython kernel install --user --name=[my-env-name]
```

## Installing a development environment

The install instructions are slightly different to create a development environment compared to a user environment:

--8<-- "README.md:docs-install-dev"

For more detailed installation instructions specific to developing the h3xplorer codebase, see our [development documentation][setting-up-a-development-environment].
