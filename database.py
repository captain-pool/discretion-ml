import os

import faiss
import numpy as np

class Database(object):
  def __init__(self, db_path, vector_dim):
    name = os.path.basename(db_path)
    path = os.path.normpath(db_path)
    if not os.path.exists(path) or not os.path.isdir(path):
      os.makedirs(path)
    self._index_file = os.path.join(path, "%s.index" % name)
    self._docs_path = os.path.join(path, "%s.docs" % name)
    self._vector_dim = vector_dim

  def open(self):
    if os.path.exists(self._index_file) and os.path.exists(self._docs_path):
      self._index = faiss.read_index(self._index_file)
      with open(self._docs_path, "rb") as f:
        self._docs = np.load(f)
      assert self._index.ntotal == len(self._docs),\
             "Number of Rows doesn't match"
      return
    print("No database found. Initializing a new one")
    self._index = faiss.IndexFlatL2(self._vector_dim)
    self._docs = np.asarray([], dtype=str)

  def search(self, vector, num_closest=1):
    if len(vector.shape) < 2:
      vector = vector[np.newaxis, :]
    _, index = self._index.search(vector, num_closest)
    docs_paths = self._docs[tuple(index)]
    return docs_paths.tolist()
  
  def insert(self, string, vector):
    if len(vector.shape) < 2:
      vector = vector[np.newaxis, :]
    self._index.add(vector)
    self._docs = np.append(self._docs, string)
  
  def remove(self, index):
    index = np.asarray(index)
    if index.ndim < 1:
      index = index[np.newaxis, :]
    self._docs = np.delete(self._docs, index)
    self._index.remove(index)

  def write(self):
    faiss.write_index(self._index, self._index_file)
    with open(self._docs_path, "wb") as f:
      np.save(f, self._docs)
