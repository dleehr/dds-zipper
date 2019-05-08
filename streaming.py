import requests
import zipstream
from flask import Flask, Response
app = Flask(__name__)

# list of urls
# create a zip file
# stream it
# add each url

urls = [
  ('https://raw.githubusercontent.com/Duke-GCB/bespin-api/master/Dockerfile', 'bespin-api/Dockerfile'),
  ('https://raw.githubusercontent.com/Duke-GCB/bespin-api/master/requirements.txt', 'bespin-api/requirements.txt'),
  ('https://github.com/allanlei/python-zipstream/archive/master.zip', 'zipstream/master.zip'),
  ]

def fetch(url):
  print('FETCH {}'.format(url))
  r = requests.get(url, stream=True)
  for chunk in r.iter_content(chunk_size=None):
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
