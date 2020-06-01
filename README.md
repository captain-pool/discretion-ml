# Dis-cretion ML
Machine Learning Backend of Dis-cretion an automated platform for helping
HR do jobs.

# prepping environment
```bash
$ wget <link to miniconda for python 3.x> -O miniconda.sh
$ bash miniconda.sh
$ conda env create --file environment.yml
$ conda activate discretion
$ conda update -c conda-forge conda
$ pip install -r requirements.txt
$ python -m spacy download <model_name/ preferably en_core_wb_sm>
```
# Crawling Policy Documents and Responses
```bash
$ ./crawl <context_name> --host <mongo_host> -p <mongo_port>
```

# Launching the backend

```bash
$ ./launch_server.sh <context_name> -mp <mongo port> -mh <mongo host>
```

