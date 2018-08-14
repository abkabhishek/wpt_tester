import requests


class APIman:

    def __init__(self):
        self.validate = Validate()
    @classmethod
    def send(cls, method, url, **kwargs):
        r = requests.request(method, url, **kwargs)
        return r

class Validate:

    def __init__(self):
        pass

    def status(self, res, expectedStatusCode):
        try:
            if (isinstance(expectedStatusCode, str)):
                raise Exception("int should be passed")
            assert (res.status_code == expectedStatusCode)
        except AssertionError:
            return False
        except Exception as err:
            return "Incorrect code type " + repr(err)
        return True

if __name__ == "__main__":
    obj = APIman()
    url = 'https://restcountries.eu/rest/v2/name/united'
    r = obj.send('GET', url)
    print(obj.validate.status(r, 200))