# NIPTool  [![Coverage Status](https://coveralls.io/repos/github/Clinical-Genomics/NIPTool/badge.svg?branch=master)](https://coveralls.io/github/Clinical-Genomics/NIPTool?branch=master) [![Build Status](https://travis-ci.org/Clinical-Genomics/NIPTool.svg?branch=master)](https://travis-ci.org/Clinical-Genomics/NIPTool) ![Latest Release](https://img.shields.io/github/v/release/clinical-genomics/NIPTool)


NIPTool is a visualisation tool for NIPT data.

## Installation


```bash
git clone https://github.com/Clinical-Genomics/NIPTool.git
cd NIPTool
pip install -r requirements.txt -e .
```

## Usage

### Demo

Once installed, you can setup NIPTool by running a few commands using the included command line interface. Given you have a MongoDB server listening on the default port (27017), this is how you would setup a fully working NIPTool demo:

```bash
nipt -c NIPTool/tests/fixtures/nipt_config.yaml load batch -b NIPTool/tests/fixtures/valid_fluffy.csv
nipt -c NIPTool/tests/fixtures/nipt_config.yaml load user -n <mane> -r RW -e <mail>
```

This will setup an instance of NIPTool with a database called `nipt-demo`. Now run

```bash
nipt run
```
And play around with the interface.

### Docker image

NIPTool can be runned also as a container. The image is available [on Docker Hub](https://hub.docker.com/repository/docker/clinicalgenomics/niptool) or can be build using the Dockerfile provided in this repository.

To build a new image from the Dockerfile use the commands: `docker build -t niptool .`

To run the image use the following command: `docker run --name niptool niptool nipt `

To remove the container, type: `docker rm niptool`


## Release model
NIPTool development is organised on a flexible Git "Release Flow" branching system. This more or less means that we make releases in release branches which corresponds to stable versions of NIPTool.

### Steps to make a new release:

1) Create a release branch from master named `version_X.X.X`
2) Update change log with the new version.
3) Update NIPTool/__init__.py with the new version.
4) Make a PR to master,
	- Name PR `release version X.X.X`
	- Justify if its a patch/minor/major version bump
	- Paste the latest changelog to the text body
	- get it approved and merge to master. **Dont delete the release branch!**
5) Make a [new release](https://github.com/Clinical-Genomics/NIPTool/releases/new).
	- Name tag version as `vX.X.X`
	- Set target to the release branch
	- Make descriptive title
	- Paste latest changelog to the text body
	- Release!

### Deploying to production

Use `update-nipt-prod.sh` script to update production both on Hasta and clinical-db. **Please follow the development guide and `servers` repo when doing so. It is also important to keep those involved informed.**

## Back End
The NIPT database is a Mongo database consisting of following collections:

- **batch** - holds batch level information.
- **sample** - holds sample level information.
- **user** - holds user names, emails and roles.

The database is loaded through the CLI with data generated by the [FluFFyPipe](https://github.com/Clinical-Genomics/fluffy).

## CLI
The CLI has two base commands - load and run. The load command is for loading batch and sample data into the nipt database, and the run command is for running the web application.

### Load


```
Usage: nipt -c <config.yaml> load batch  [OPTIONS] ...
```



### Run
```
Usage: nipt run [OPTIONS] ...

```
