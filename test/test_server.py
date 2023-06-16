
import sys, os
from fastapi.testclient import TestClient
sys.path.append(f"{os.pardir}/filerouter/")
from config import config_org

app_data_path = config_org.app_data_path
name_zip = 'abc.zip'

from server import app
testclient = TestClient(app)

def test_read_main():
    res = testclient.get('')
    assert res.status_code == 200
    assert type(res.json()) == dict

def test_zip():

    with open(f"{app_data_path}/{name_zip}", "rb") as _file:
        res = testclient.post("/zip?test=1", files={"file": (f"{name_zip}", _file, "application/zip")})
    print("/zip:", res.status_code)
    print("/zip:", res.json())
    assert res.status_code == 200
    assert type(res.json()) == dict


def test_files():

    with open(f"{app_data_path}/aaa.txt", "rb") as file_zip, \
         open(f"{app_data_path}/bbb.txt", "rb") as file_image, \
         open(f"{app_data_path}/ccc.txt", "rb") as file_video:

        files = [
            ('files', file_zip),
            ('files', file_image),
            ('files', file_video)
        ]
        res1 = testclient.post("/files?test=1", files=files)
        print('/files', res1.status_code)
        print('/files', res1.json())
        assert res1.status_code == 200
        assert type(res1.json()) == dict


        res2 = testclient.post("/files-bytesio?test=1", files=files)
        print('/files', res2.status_code)
        print('/files', res2.json())
        assert res2.status_code == 200
        assert type(res2.json()) == dict


if __name__ == "__main__":

    test_read_main()

    test_files()

    test_zip()
