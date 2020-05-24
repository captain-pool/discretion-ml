import spacy

class Vectorize(object):
  def __init__(self, model="en_core_web_sm"):
    self._model_name = model
  def open(self):
    self._vmodel = spacy.load(self._model_name)
  def vectorize(self, sentence):
    return self._vmodel(sentence).vector
