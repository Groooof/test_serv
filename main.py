from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pydantic as pd   
from zipfile import ZipFile
import os
import uuid
import typing as tp


def get_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins='*',
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    return app


class DicomImportRequest(pd.BaseModel):
    filename: str


app = get_app()


class CTStorage:
    _CT_DIR = './ct'    
    
    @classmethod
    def save(cls, ct_data: tp.Union[ZipFile, tp.Any]) -> uuid.UUID:
        foldername, path = cls._gen_path()
        
        if isinstance(ct_data, ZipFile):
            is_correct_zip = cls._check_zip(ct_data)
            if not is_correct_zip:
                return None
            
            ct_data.extract(ct_data.infolist()[1], path)
            return foldername
        
    
    @classmethod
    def load(cls, foldername: str):
        pass
    
    @classmethod
    def _gen_path(cls) -> tp.Tuple[uuid.UUID, str]:
        foldername = uuid.uuid4()
        path = cls._CT_DIR + '/' + foldername.hex[:2] + '/' + foldername.hex
        return foldername, path
    
    def _check_zip(zip_file: ZipFile):
        folder = zip_file.filelist[0]
        if not folder.is_dir():
            return False
        for item in zip_file.infolist()[1:]:
            if item.filename.startswith(folder.filename) and item.filename.count('/') == 1 and check_dicom_ext(item.filename):
                continue
            return False
        return True
    
    
def get_file_ext(filename: str):
    return os.path.splitext(filename)[1]
    
    
def check_dicom_ext(filename: str):
    dicom_ext = '.dcm'
    return get_file_ext(filename) == dicom_ext
    
    
def check_zip_ext(filename: str):
    zip_ext = '.zip'
    return get_file_ext(filename) == zip_ext
    
    

@app.get('/dicom/import')
def dicom_import():
    return FileResponse('./dicom/test_1.dcm')


@app.post('/dicom/export')
def dicom_export(file: UploadFile):
    is_zip = check_zip_ext(file.filename)
    is_dicom = check_dicom_ext(file.filename)
    if is_zip:
        zip_file = ZipFile(file.file)
        foldername = CTStorage.save(zip_file)
        return foldername
        
    if is_dicom:
        pass

    
    
    # print(file.filename)
    
