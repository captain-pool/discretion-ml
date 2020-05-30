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
$ python doc_crawler.py -cfg configs/*yaml -t P \
         -m <spacy_model_name> \
         -ctx <context_name>
```

#Launching the backend

```bash
$ python3 discretion.py -cfg configs/*yaml \
                        -ctx <context_name> \
                        -m <spacy_model_to_use> \
                        -p <port of server> --host <host IP>
```

