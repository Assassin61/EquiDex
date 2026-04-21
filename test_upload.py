import urllib.request, json

boundary = 'FairProbeTest123'
csv_content = (
    b'name,age,ethnicity,experience,gpa,decision,score\r\n'
    b'James Smith,30,Caucasian,5,3.5,accepted,75\r\n'
    b'Mohammed Hassan,28,Middle Eastern,5,3.5,rejected,44\r\n'
    b'Lakisha Williams,27,African American,4,3.6,rejected,38\r\n'
    b'Emily White,29,Caucasian,4,3.4,accepted,70\r\n'
    b'Priya Sharma,31,South Asian,6,3.7,rejected,40\r\n'
)

body = (
    ('--' + boundary + '\r\n').encode() +
    b'Content-Disposition: form-data; name="file"; filename="test.csv"\r\n' +
    b'Content-Type: text/csv\r\n\r\n' +
    csv_content +
    ('\r\n--' + boundary + '--\r\n').encode()
)

req = urllib.request.Request(
    'http://127.0.0.1:8000/audit/upload',
    data=body,
    headers={'Content-Type': 'multipart/form-data; boundary=' + boundary},
    method='POST'
)
r = urllib.request.urlopen(req)
result = json.loads(r.read())
print('Upload result:')
print(json.dumps(result, indent=2))
