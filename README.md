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
UF_Grant_Data.json
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
The following command will bindmount the directory called input in your current user's home directory to /var in the container. The ~/input directory must contain the input json file and the config.yaml file to be used by the program.

The config file must contain the correct IP address of the VIVO server.

### What the code does?
The code loads the Grant data from an input JSON file into the VIVO Graph database. It uses the `vivo_queries` and `owpost` libraries as reference.

The code parses the JSON file and uses the following mapping to load the data into VIVO.

| VIVO Field         | Field in JSON file                                    |
|--------------------|-------------------------------------------------------|
| awarded_by         | reporting_sponsor_name                                |
| data/time interval | clk_awd_overall_start_date / clk_awd_overall_end_date |
| administered_by    | clk_awd_prime_sponsor_name                            |
| total_award_amount | sponsor_authorized_amount                             |
| direct_costs       | direct_amount                                         |
| contributor        | clk_awd_pi                                            |
| local_award_id     | clk_awd_id                                            |
| sponsor_award_id   | clk_awd_sponsor_awd_id                                |
| title              | clk_awd_full_title                                    |

### Note: 
If we perform bulk load of grants data using the API, it takes time to for the Grants to reflect on the VIVO portal (while running on localhost using vivo vagrant). Sometime, it does not show up as well. For validation purpose, one can always check for the Grants that are being loaded by running the following SPARQL query:

```sparql
SELECT ?grant ?g_label
WHERE {
  ?grant <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Grant> .
  ?grant <http://www.w3.org/2000/01/rdf-schema#label> ?g_label
 
}
```

