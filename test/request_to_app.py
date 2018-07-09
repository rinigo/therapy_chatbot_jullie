import requests


def post_to_webhook(url, times):
    """
        url
            jullie-dev-pr-336:
                https://jullie-dev-pr-336.herokuapp.com/
            jullie-dev:
                https://jullie-dev.herokuapp.com/
        """
    headers = {
        'Content-Type': 'application/json',
    }

    for i in range(0, times):
        data = """{
            "object":"page",
            "entry":[
                {
                    "id":43674671559,
                    "time":1460620433256,
                    "messaging":[
                        {
                            "sender":{
                                "id": """ + str(i) + """
                            },
                            "recipient":{
                                "id":221043008462492
                            },
                            "timestamp":1460620433123,
                            "message":{
                                "mid":"mid.1460620432888:f8e3412003d2d1cd93",
                                "seq":12604,
                                "text": "test""" + str(i) + "\"" """
                            }
                        }
                    ]
                }
            ]
        }"""
        print(i)
        requests.post(url, headers=headers, data=data)
