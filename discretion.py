import os
import json

import argparse
import flask
import flask_cors
import config
import database
import doc_crawler
import vectorizer

class Discretion(object):
  def __init__(self, args):
    self._app = flask.Flask(__name__)
    flask_cors.CORS(self._app)
    self._vect_model = vectorizer.Vectorize(args.vmodel)
    self._config = config.Config(args, args.config, orphan=True)
    if not self._config.get(args.ctx):
      raise AttributeError(f"Context name not valid: {args.ctx}")
    self._policy_db = database.Database(
        self._config[args.ctx].databases.policy,
        self._config[args.ctx].vector_dim.policy)
    self._response_db = database.Database(
        self._config[args.ctx].databases.response,
        self._config[args.ctx].vector_dim.response)
    self._ctx_name = args.ctx
    self._route_set = False

  @staticmethod
  def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", dest="vmodel", required=True,
                        help="spaCy model to use for Vectorization")
    parser.add_argument("-cfg", dest="config", nargs="+", required=True,
                        type=os.path.normpath, help="Path to config files")
    parser.add_argument("-ctx", type=str, required=True, help="Context to use")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="IP of the host")
    parser.add_argument("-p", "--port", type=int, help="Port to use",
                        default=8080)
    return parser

  def search(self):
    """
      Searches the Similarity Database.
      Request: List of Entries of the Row. Columns should be similar to
               the Google Docs. Column Name not employed, only the values
               for each column.
      Response: json of the following form.
                {
                  "poldocs": [<docs link to similar policy docs>, . . .],
                  "cases": [{
                              "url": <sheets link to similar case>,
                              "rownum": <row number of the entry>
                            }, . . .(similar json objects for multiple cases)]
                 }
    """
    row = flask.request.json.get("row", None) # TODO(@captain-pool): choose b/w flask.request.args and flask.request.json
    count = flask.request.json.get("count", 1) # TODO(@captain-pool): choose b/w flask.request.args and flask.request.json
    related_policy_docs = []
    related_cases = []
    if row:
      # row = json.loads(row)
      ref_vector = doc_crawler.vectorize_row(row, self._vect_model)
      policy_vector = self._vect_model.vectorize(" ".join(row))
      related_policy_docs = self._policy_db.search(policy_vector, count)
      related_cases = self._response_db.search(ref_vector, count)
    return flask.jsonify({
        "poldocs": related_policy_docs,
        "cases": related_cases
        })

  def dummy_response(self):
    return "Server Running"

  def spawn_server(self):
    if not self._route_set:
      self._app.route(rule=f"/{self._ctx_name}", methods=["POST"])(self.search)
      self._app.route(rule="/", methods=["GET"])(self.dummy_response)
      self._route_set = True
    self._vect_model.open()
    self._policy_db.open()
    self._response_db.open()
    self._app.run(
        self._config["host"],
        self._config["port"])

if __name__ == "__main__":
  parser = Discretion.build_parser()
  discretion = Discretion(parser.parse_args())
  discretion.spawn_server()
