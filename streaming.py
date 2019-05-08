import requests
import zipstream
from flask import Flask, Response
app = Flask(__name__)

# list of urls
# create a zip file
# stream it
# add each url

urls = [
  ('http://hgdownload.cse.ucsc.edu/goldenpath/hg38/bigZips/hg38.fa.gz', 'bigZips/hg38.fa.gz'),
  ('http://hgdownload.cse.ucsc.edu/goldenpath/hg38/bigZips/hg38.fa.masked.gz', 'bigZips/hg38.fa.masked.gz'),
  ('http://hgdownload.cse.ucsc.edu/goldenpath/hg38/bigZips/hg38.fa.out.gz', 'bigZips/hg38.fa.out.gz'),
  ]

def fetch(url):
  print('FETCH {}'.format(url))
  r = requests.get(url, stream=True)
  for chunk in r.raw.stream():
    print('RECEIVE {}'.format(len(chunk)))
    yield chunk

def stream():
  z = zipstream.ZipFile()
  for (url, filename) in urls:
    print('write_iter {}'.format(filename))
    z.write_iter(filename, fetch(url))
  return z

# write_iter takes a name and a function that yields bytes from a file
# write_iter(arcname, iterable, compress_type=None, buffer_size=None) method of zipstream.ZipFile instance
#    Write the bytes iterable `iterable` to the archive under the name `arcname`.
# z.write_iter()

@app.route("/zipfile.zip", methods=['GET'], endpoint='zipfile')
def zipfile():
  def generate():
    z = stream()
    for chunk in z:
      print('WRITE {}'.format(len(chunk)))
      yield chunk

  response = Response(generate(), mimetype='application/zip')
  response.headers['Content-Disposition'] = 'attachment; filename={}'.format('zipfile.zip')
  print('RESPOND')
  return response
