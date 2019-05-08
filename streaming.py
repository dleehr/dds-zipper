import requests
import zipstream

# list of urls
# create a zip file
# stream it
# add each url

urls = [
  ('https://raw.githubusercontent.com/Duke-GCB/bespin-api/master/Dockerfile', 'Dockerfile')
  ]

def fetch(url):
  print('fetching', url)
  for _ in range(10):
    yield b'bytes'

z = zipstream.ZipFile()

for (url, filename) in urls:
  z.write_iter(filename, fetch(url))
  print('wrote', filename)


# finally, write the zipfile
with open('zipfile.zip', 'wb') as f:
  for data in z:
    f.write(data)

# write_iter takes a name and a function that yields bytes from a file
# write_iter(arcname, iterable, compress_type=None, buffer_size=None) method of zipstream.ZipFile instance
#    Write the bytes iterable `iterable` to the archive under the name `arcname`.
# z.write_iter()
