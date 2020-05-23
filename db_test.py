import database
import numpy as np
db = database.Database("tempdb", 10)
data = np.random.normal(size=[1, 10]).astype(np.float32)
db.open()
db.insert("Bobby", data)
search = np.random.normal(size=[1, 10]).astype(np.float32)
db.write()
print(db.search(search, 10))
