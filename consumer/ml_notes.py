conn = psycopg2.connect(dbname="results", user="defaultclassifier", password="mldefault",host="10.0.0.10")
cur.execute("INSERT INTO sessions (sess_id, ml_model, preprocessing) VALUES (%s, %s, %s)", ("testSession2","testML","testPreprocessing"))
