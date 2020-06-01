import os

import argparse
import config
import database
import json
import glob
import gspread
import vectorizer
import pandas as pd
import numpy as np
import tqdm
import hashlib, base64, datetime
import re
import pymongo
from bson import objectid


def build_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument("-cfg", "--configs", nargs="+", type=os.path.normpath,
                      required=True, help="Path to configuration files")
  parser.add_argument("-t", type=str, required=True,
                      help="Type of Document ([P]olicy/ [R]esponse)")
  parser.add_argument("-m", dest="vmodel", type=str, required=True,
                      help="spaCy model to use")
  parser.add_argument("-ctx", "--context", type=str, required=True,
                     help="Context")
  parser.add_argument('--host', dest="host", type=str, default='localhost',
                      help="Host address for mongodb")
  parser.add_argument('-p', dest="port", type=int, default=27017,
                      help="Port of mongodb server")
  return parser

def get_random_id(length=6):
  timestamp = datetime.datetime.now()
  b64encoded = base64.b64encode(
      hashlib.sha256(str(timestamp).encode("utf-8")).digest())
  b64encoded = re.sub("[+/=]", "", b64encoded.decode("utf-8"))
  return b64encoded[:length].upper()

def ispolicy(type_):
  return type_.lower() == "p" or type_.lower() == "policy"

def isresponse(type_):
  return type_.lower() == "r" or type_.lower() == "response"

def iterate_sheets(gc, ids):
  for id_ in ids:
    sheet = gc.open_by_key(id_).sheet1
    data = sheet.get_all_values()
    headers = data.pop(0)
    dataframe = pd.DataFrame(data, columns=headers).iloc[:, :-2]
    dataframe.drop(columns=['ending_displayed_id'], inplace=True)
    dataframe.columns = [
        'summary',
        'situation',
        'arrangement',
        'anything_else',
        'email',
        'firstname']
    yield dataframe

def insert_sheets_to_db(vct_model, ids, db, collection, config):
  gc = gspread.service_account(filename=os.environ['KEY'])
  sheets = iterate_sheets(gc, ids)
  for sheet in tqdm.tqdm(sheets, position=0):
    for id_, row in tqdm.tqdm(sheet.iterrows()):
      vct = vectorize_row(row.tolist()[:-2], vct_model)
      row['decision'] = 'notdecided'
      payload = row.to_dict()
      token = get_random_id()
      payload.update({"token": token})
      collection.insert_one(payload)
      db.insert(token, vct)
  db.write()

def vectorize_row(row, vct_model):
  vct = []
  for entry in row:
    if not entry:
      entry = "NA"
    vct.append(vct_model.vectorize(entry))
  return np.hstack(vct)

def vectorize_policy_docs(vct_model, dir_, db):
  for text_file in tqdm.tqdm(glob.glob(os.path.join(f"{dir_}/*.txt"))):
    with open(text_file) as f:
      data = f.read()
      drive_id, _ = os.path.basename(text_file).split(".txt")
      url = f"https://docs.google.com/document/d/{drive_id}"
    db.insert(url, vct_model.vectorize(data))
  db.write()

def main(argv):
  db = None
  cfg = config.Config(argv, argv.configs, orphan=True)
  print(cfg)
  connection = pymongo.MongoClient(cfg.host, cfg.port)
  vct_model = vectorizer.Vectorize(cfg.vmodel)
  ctx_name = cfg.context
  if not cfg.get(ctx_name):
    raise AttributeError(f"Context not understood: {ctx_name}")
  if ispolicy(cfg.t):
    db = database.Database(cfg[ctx_name].databases.policy,
                           cfg[ctx_name].vector_dim.policy)
  if isresponse(cfg.t):
    db = database.Database(cfg[ctx_name].databases.response,
                           cfg[ctx_name].vector_dim.response)
  if not db:
    raise AttributeError(f"Database cannot be found of the" \
                          "given type: {cfg.t}")
  vct_model.open()
  db.open()
  if ispolicy(cfg.t):
    vectorize_policy_docs(vct_model, cfg[ctx_name].dir, db)
  else:
    mongodb = connection[ctx_name]
    if ctx_name not in connection.list_database_names():
      mongodb.create_collection('response')
    collection = mongodb['response']
    insert_sheets_to_db(vct_model, cfg[ctx_name].ids, db, collection, cfg)

if __name__ == "__main__":
  parser = build_parser()
  args = parser.parse_args()
  main(args)
