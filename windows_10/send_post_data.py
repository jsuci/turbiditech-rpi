import http.client
import mimetypes
from codecs import encode
from base64 import b64encode

conn = http.client.HTTPSConnection("turbiditech.fly.dev")
dataList = []
boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=valve_status;'))
# dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))
dataList.append(encode("off"))

dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=water_status;'))
# dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))
dataList.append(encode("clean"))

dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=record_device;'))
# dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))
dataList.append(encode("2"))

dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=details;'))
# dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))
dataList.append(encode("Device has set the valve status to ON and set water status to DIRTY"))

dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=record_image; filename={0}'.format('../images/test.jpg')))
# fileType = mimetypes.guess_type('../images/test.jpg')[0] or 'application/octet-stream'
# dataList.append(encode('Content-Type: {}'.format(fileType)))
dataList.append(encode(''))

with open('../images/test.jpg', 'rb') as f:
    dataList.append(f.read())
    dataList.append(encode('--'+boundary+'--'))
    dataList.append(encode(''))

body = b'\r\n'.join(dataList)
payload = body
user = 'jsuci.jsuci@gmail.com'
password = 'admin'
headers = {
  'Authorization': f'Basic {b64encode(bytes(f"{user}:{password}", "utf-8")).decode("ISO-8859-1")}',
  'Content-type': f'multipart/form-data; boundary={boundary}'
}
conn.request("POST", "/api/device-records/2", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))