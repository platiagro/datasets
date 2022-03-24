import os
from datasets.api import app
from fastapi.testclient import TestClient

os.environ["ENABLE_CORS"] = "1"

TEST_CLIENT = TestClient(app)

PATH_DEFAULT = f"{os.getcwd()}/samples"
FILENAME_TARGET = 'iris_vazio.csv'
FILENAME_TARGET_NOT_EXISTS = ''

_UPLOAD_FILE = f'{PATH_DEFAULT}/{FILENAME_TARGET}'

ROUTER = '/datasets'


class TestValidateUploadFile:
    def test_file_empty(self):
        _file = {'file': open(_UPLOAD_FILE, 'rb')}

        response = TEST_CLIENT.post(f"{ROUTER}", files=_file)

        assert response.status_code == 400
        assert response.json() == {"detail": "File content is empty or blank"}

    def test_file_not_exists(self):
        _file = FILENAME_TARGET_NOT_EXISTS

        response = TEST_CLIENT.post(f"{ROUTER}", files=_file)

        assert response.status_code == 400
        assert response.json() == {"detail": "File not exists"}

    def test_file_not_exists_blank(self):
        _file = {'file': FILENAME_TARGET_NOT_EXISTS}

        response = TEST_CLIENT.post(f"{ROUTER}", files=_file)

        assert response.status_code == 400
        assert response.json() == {"detail": "File content is empty or blank"}
