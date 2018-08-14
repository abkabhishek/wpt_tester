from mailjet_rest import Client
import os

'''This call sends a message to the given recipient with attachment.'''


API_KEY = ''
API_PASS = ''

MAILJET= Client(auth=(api_key, api_secret), version='v3.1')

data = {
        'Messages': [
                {
                        "From": {
                                "Email": "pilot@mailjet.com",
                                "Name": "Mailjet Pilot"
                        },
                        "To": [
                                {
                                        "Email": "passenger1@mailjet.com",
                                        "Name": "passenger 1"
                                }
                        ],
                        "Subject": "Your email flight plan!",
                        "TextPart": "Dear passenger 1, welcome to Mailjet! May the delivery force be with you!",
                        "HTMLPart": "<h3>Dear passenger 1, welcome to Mailjet!</h3><br />May the delivery force be with you!",
                        "Attachments": [
                                {
                                        "ContentType": "text/plain",
                                        "Filename": "test.txt",
                                        "Base64Content": "VGhpcyBpcyB5b3VyIGF0dGFjaGVkIGZpbGUhISEK"
                                }
                        ]
                }
        ]
}


result = mailjet.send.create(data=data)

return  result.status_code
# print result.json()
