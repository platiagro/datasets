from typing import Optional
from fastapi import File, UploadFile, HTTPException
from pydantic import BaseModel, validator


class FileUploadValidate(BaseModel):
    name: Optional[str] = ""
    size: Optional[int]
    file: UploadFile = File(None)

    class Config:
        validate_assignment = True

    @validator('file')
    def check_file_exists(cls, file: UploadFile, values, **kwargs):
        if not file:
            raise HTTPException(status_code=400, detail="File not exists")

        contents = file.file.read()
        if isinstance(len(contents), int) and len(contents) <= 0:
            raise HTTPException(status_code=400, detail="File content is empty or blank")

        values["size"] = len(contents)
        values["name"] = file.filename
        return file

    @validator('size')
    def check_size_is_empty(cls, value):
        if isinstance(value, int) and value <= 0:
            raise HTTPException(status_code=400, detail="File content is empty or blank")
        return value

    @validator('name')
    def get_filename(cls, value):
        if not value:
            raise HTTPException(status_code=400, detail="Filename not exists")
        return value
