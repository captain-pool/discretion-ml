import argparse
import config
import gspread
import vectorizer
import pandas as pd


def build_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument("-configs", nargs="+", type=os.path.normpath, required=True,
                      "Path to configuration files")
  parser.add_argument("-c", "--clientkey", type=str, required=True,
                      help="Client Key of the Service Account")
  parser.add_argument("-id", nargs="+", type=str,
                      help="IDs of the Google Sheets")
  parser.add_argument("-t", type=str, required=True,
                      help="Type of Document ([P]olicy/ [R]esponse)")
  parser.add_argument("-m", target="vmodel", type=str, required=True,
                      help="spaCy model to use")
  parser.add_argument("-d", target="dir", type=str,
                      help="Directory with txt versions of policy docs")
  return parser

def ispolicy(type_):
  return type_.lower() == "p" or type_.lower() == "policy"

def isresponse(type_):
  return type_.lower() == "r" or type_.lower() == "response"

def iterate_sheets(gc, ids):
  for id_ in ids:
    sheets = gc.open_by_key(id_).sheet1
    data = sheets.get_all_values()
    headers = data.pop(0)
    dataframe = pd.DataFrame(data, columns=headers)
    yield dataframe

def vectorize_sheets(vct_model, ids, db):
  gc = gspread.service_account(filename=os.environ.get('KEY'))
  sheets = iterate_sheets(ids)
  for sheet in sheets:
    pass
    #TODO(@captain-pool): Add Sheet Vectorizing Logic Here

def vectorize_policy_docs(vct_model, dir_, db):
  for text_file in glob.glob(os.path.join(f"{dir_}/*.txt")):
    with open(text_file) as f:
      data = f.read()
    db.insert(data, vct_model.vectorize(data))

def main(argv):
  db = None
  config = config.Config(argv.configs)
  vct_model = Vectorize(config.vmodel)
  if ispolicy(config.t):
    db = database.Database(config.databases.hr,
                           config.vector_dim.policy)
  if isresponse(config.t):
    db = database.Database(config.databases.responses,
                           config.vector_dim.response)
  if not db:
    raise AttributeError(f"Database cannot be found of the" \
                          "given type: {config.t}")
  vct_model.open()
  if ispolicy(config.t):
    vectorize_policy_docs(vct_model, config.dir, db)
  else:
    vectorize_sheets(vct_model, config.id, db)

if __name__ == "__main__":
  parser = build_parser()
  args = parser.parse_args()
  main(args)
