import requests
import zipstream
from ddsc.sdk.client import Client, PathToFiles
from ddsc.config import Config

from flask import Flask, Response
app = Flask(__name__)

# project_id = 'ea4b60ed-b145-49ab-a41f-6ae122e06630' # bigger
project_id = '20c1b14c-91c6-4a30-ab5e-aec4d632ee65'
my_token = ''

urls = [
  ('http://hgdownload.cse.ucsc.edu/goldenpath/hg38/bigZips/hg38.fa.gz', 'bigZips/hg38.fa.gz'),
  ('http://hgdownload.cse.ucsc.edu/goldenpath/hg38/bigZips/hg38.fa.masked.gz', 'bigZips/hg38.fa.masked.gz'),
  ('http://hgdownload.cse.ucsc.edu/goldenpath/hg38/bigZips/hg38.fa.out.gz', 'bigZips/hg38.fa.out.gz'),
  ]

def make_config(token):
  c = Config()
  c.update_properties({Config.AUTH: token})
  return c

def get_url(client, dds_file):
  print('GETURL')
  # This is a time-sensitive call, so we should only do it right before fetch
  fd = client.dds_connection.get_file_download(dds_file.id)
  return '{}{}'.format(fd.host, fd.url)

def fetch(client, dds_file):
  url = get_url(client, dds_file)
  print('FETCH {}'.format(url))
  r = requests.get(url, stream=True)
  for chunk in r.raw.stream():
    print('RECEIVE {}'.format(len(chunk)))
    yield chunk

def get_dds_paths(client, project_id):
  children = client.dds_connection.get_project_children(project_id)
  ptf = PathToFiles()
  for child in children:
    ptf.add_paths_for_children_of_node(child)
  return ptf.paths # OrderedDict of path -> File

def stream():
  z = zipstream.ZipFile()
#   config = make_config(my_token)
  client = Client()
  paths = get_dds_paths(client, project_id)
  for (filename, dds_file) in paths.items():
    print('write_iter {}'.format(filename))
    z.write_iter(filename, fetch(client, dds_file))
  return z

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

def main():
    z = stream()
    with open('zipfile.zip', 'wb') as f:
      for data in z:
        print('WRITE {}'.format(len(data)))
        f.write(data)

if __name__=='__main__':
  main()
