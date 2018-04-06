# grantload
Load grant data from csv file to VIVO

## Getting Started

These instructions will help you build a docker image on your local machine from which you can spawn up and run a container that would automate the process of grant load.

First clone the project in your local.

```
git clone -b docker_grant https://github.com/roukna/grantload.git
```

### Prerequisites

The input file should have the name following name:
```
UF_Grant_Data.csv
```


### Building the docker image

```bash
docker build -t grant_image:latest .
```
Once the image is built, you may save it as a tar file and share it.

```bash
docker save grant_image:latest | gzip -c > grant_image.tar.gz
```
For loading the image from tar.gz in another machine:

```bash
gunzip -c grant_image.tar.gz | docker load
```

### Run the image
```bash
docker run -v ~/input:/var -it grant_image:latest /bin/bash
```
The following command will bindmount the directory called input in your current user's home directory to /var in the container. The ~/input directory must contain the input csv file and the config.yaml file to be used by the program.

