import requests
import zipstream
from ddsc.sdk.client import Client, PathToFiles
from ddsc.config import Config

from flask import Flask, Response
app = Flask(__name__)

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

def build_zip(client, project_id):
  z = zipstream.ZipFile()
  paths = get_dds_paths(client, project_id)
  for (filename, dds_file) in paths.items():
    print('write_iter {}'.format(filename))
    z.write_iter(filename, fetch(client, dds_file))
  return z

def get_project_name(client, project_id):
  project = client.get_project_by_id(project_id)
  return project.name

@app.route("/download-project/<project_id>.zip", methods=['GET'])
def download(project_id):
  client = Client() # This assumes it can authenticate
  project_name = get_project_name(client, project_id)
  def generate():
    z = build_zip(client, project_id)
    for chunk in z:
      print('WRITE {}'.format(len(chunk)))
      yield chunk
  response = Response(generate(), mimetype='application/zip')
  response.headers['Content-Disposition'] = 'attachment; filename={}'.format('{}.zip'.format(project_name))
  print('RESPOND')
  return response

def main():
  project_id = '20c1b14c-91c6-4a30-ab5e-aec4d632ee65'
  client = Client()
  project_name = get_project_name(client, project_id)
  z = build_zip(client, project_id)
  with open('{}.zip'.format(project_name), 'wb') as f:
    for data in z:
      print('WRITE {}'.format(len(data)))
      f.write(data)

if __name__=='__main__':
  main()
