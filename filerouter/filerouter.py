
import os, sys
from typing import List, Union, Dict, Optional
import zipfile
import uuid
from fastapi.responses import FileResponse, JSONResponse
from fastapi import HTTPException, BackgroundTasks
from fastapi import Response, UploadFile
import io

from filerouter.logconf import frouterlogger
logger = frouterlogger(__name__)
print('__name__', __name__)
from filerouter import tools

from enum import Flag, auto


class processType(Flag):
    BYTES = auto()
    FILE = auto()


class config():
    def __init__(self, **kwargs):

        print("kwargs: ", kwargs)
        self.data_path = kwargs["data_path"] if "data_path" in kwargs.keys() else "./temp"
        # self.sleep_sec_remove = _config.SLEEP_SEC_REMOVE
        # self.sleep_sec_remove_response = _config.SLEEP_SEC_REMOVE_RESPONSE


class processor():

    def __init__(self, cfg: Optional[dict]):
        pass
    
    async def post_file_process(
        self,
        process_name: str,
        files_org_info: dict,
        file_dst_path: Optional[str] = None,
        bgtask: BackgroundTasks=BackgroundTasks(),
        **kwargs
    ):
        raise NotImplementedError()


def preprocess_zip(path, fname, bgtask):
    path_dir_export = f"{path}/{os.path.splitext(fname)[0]}"
    os.makedirs(path_dir_export)
    bgtask.add_task(tools.remove_dir, path_dir_export)
    with zipfile.ZipFile(f"{path}/{fname}") as zf:
        zf.extractall(path = path_dir_export)
    bgtask.add_task(tools.remove_dir, path_dir_export)


class router():
    def __init__(
        self,
        processor: processor,
        config: config
    ):

        self.processor = processor
        self.config = config
        self.data_path = config.data_path
        os.makedirs(self.path_data, exist_ok=True)
        

    async def _post_files(
        self,
        process_name: str,
        files: list[UploadFile],
        retfile_extension: Optional[str] = None,
        bgtask: BackgroundTasks = BackgroundTasks(),
        **kwargs
    ):
        
        logger.info("post_files")
        test = kwargs['test'] if 'test' in kwargs.keys() else 0
        
        uuid_path = f"{self.path_data}/{str(uuid.uuid4())}"
        os.makedirs(uuid_path)
        files_org_info = list()
        for file in files:

            logger.info(f'{file.filename}, {file.content_type}')
            fname_org = file.filename
            fname, _ = tools.fname2uuid(fname_org)
            tools.save_file(uuid_path, fname, file, test)

            files_org_info.append(
                dict(
                    path=f"{uuid_path}/{fname}",
                    name_org=fname_org,
                )
            )
            
        bgtask.add_task(tools.remove_dir, uuid_path)

        if retfile_extension is not None:
            fname_dst = tools.make_fname_uuid(retfile_extension)
            file_dst_path = f"{uuid_path}/{fname_dst}"
            bgtask.add_task(tools.remove_file, file_dst_path)
        else:
            file_dst_path = None

        data = dict(
            file=files_org_info,
            file_dst_path=file_dst_path
        )
        result = await self.processor.post_file_process(
            process_name,
            data,
            file_dst_path,
            bgtask,
            **kwargs
        )
        
        if type(file_dst_path) is str:
            if os.path.exists(file_dst_path):
                return self.post_processing(file_dst_path, **kwargs)
            else:
                return result
        else:
            return result


    async def _post_file(
        self,
        process_name: str,
        file: UploadFile,
        retfile_extension: Optional[str] = None,
        bgtask: BackgroundTasks = BackgroundTasks(),
        **kwargs
    ):
        logger.info("post_file")
        test = kwargs['test'] if 'test' in kwargs.keys() else 0
        uuid_path = f"{self.path_data}/{str(uuid.uuid4())}"
        os.makedirs(uuid_path)
        fname_org = file.filename
        ftype_input = tools.check_filetype(fname_org)
        fname, _ = tools.fname2uuid(fname_org)
        tools.save_file(uuid_path, fname, file, test)
        file_org_info = dict(
            path=f"{uuid_path}/{fname}",
            name_org=fname_org,
        )

        bgtask.add_task(tools.remove_dir, uuid_path)
        if ftype_input == tools.FileType.ZIP:
            preprocess_zip(uuid_path, fname, bgtask)
            
        if retfile_extension is not None:
            fname_dst = tools.addstr2fname(fname, "-res", ext=retfile_extension)
            file_dst_path = f"{uuid_path}/{fname_dst}"
        else:
            file_dst_path = None
        
        data = dict(
            file=file_org_info,
            file_dst_path=file_dst_path
        )
        result = await self.processor.post_file_process(
            process_name,
            data,
            file_dst_path,
            bgtask,
            **kwargs
        )
        
        if type(file_dst_path) is str:
            if os.path.exists(file_dst_path):
                return self.post_processing(file_dst_path, **kwargs)
            else:
                return result
        else:
            return result


    async def _post_file_BytesIO(
        self,
        process_name: str,
        file: UploadFile,
        retfile_extension: Optional[str] = None,
        bgtask: BackgroundTasks = BackgroundTasks(),
        **kwargs
    ):

        logger.info("post_file_BytesIO")
        fileInfo = dict(
            name=file.filename,
            bytesio=io.BytesIO(await file.read())
        )

        if retfile_extension is not None:
            uuid_path = f"{self.path_data}/{str(uuid.uuid4())}"
            fname_dst = tools.addstr2fname(fileInfo['name'], "-res", ext=retfile_extension)
            file_dst_path = f"{uuid_path}/{fname_dst}"
        else:
            file_dst_path = None
        
        data = dict(
            file=fileInfo,
            file_dst_path=file_dst_path
        )
        result = await self.processor.post_file_process(
            process_name,
            fileInfo,
            file_dst_path,
            bgtask,
            **kwargs
        )
        if type(file_dst_path) is str:
            if os.path.exists(file_dst_path):
                return self.post_processing(file_dst_path, **kwargs)
            else:
                return result
        else:
            return result
        

    async def _post_files_BytesIO(
        self,
        process_name: str,
        files: list[UploadFile],
        retfile_extension: Optional[str] = None,
        bgtask: BackgroundTasks = BackgroundTasks(),
        **kwargs
    ):

        logger.info("post_files_BytesIO")
        files_dict = list()
        for file in files:
            fname_org = file.filename
            file_byte = io.BytesIO(await file.read())
            files_dict.append(
                dict(
                    name=fname_org,
                    bytesio=file_byte
                )
            )

        if retfile_extension is not None:
            uuid_path = f"{self.path_data}/{str(uuid.uuid4())}"
            fname_dst = tools.make_fname_uuid(retfile_extension)
            file_dst_path = f"{uuid_path}/{fname_dst}"
            bgtask.add_task(tools.remove_file, file_dst_path)
        else:
            file_dst_path = None

        data = dict(
            file=files_dict,
            file_dst_path=file_dst_path
        )
        result = await self.processor.post_file_process(
            process_name,
            data,
            file_dst_path,
            bgtask,
            **kwargs
        )
        if type(file_dst_path) is str:
            if os.path.exists(file_dst_path):
                return self.post_processing(file_dst_path, **kwargs)
            else:
                return result
        else:
            return result
    

    async def post_file(
        self,
        process_name: str,
        process_type: processType,
        file: UploadFile | list[UploadFile],
        retfile_extension: Optional[str] = None,
        bgtask: BackgroundTasks = BackgroundTasks(),
        **kwargs
    ):

        test = kwargs["test"]
        if test == 1:
            if process_type == processType.FILE:
                if type(file) is UploadFile:
                    return await self._post_file(
                        process_name,
                            file,
                            retfile_extension,
                            bgtask,
                            **kwargs
                        )
                    if type(file) is list[UploadFile]:
                        return await self._post_files(
                            process_name,
                            file,
                            retfile_extension,
                            bgtask,
                            **kwargs
                        )
                if process_type == processType.BYTESIO:
                    
                    if type(file) is UploadFile:
                    return await self._post_file_bytesio(
                        process_name,
                            file,
                            retfile_extension,
                            bgtask,
                            **kwargs
                        )
                    if type(file) is list[UploadFile]:
                        return await self._post_files_bytesio(
                            process_name,
                            file,
                            retfile_extension,
                            bgtask,
                            **kwargs
                        )
        else:   
            try:
                return await self._post_file(
                    process_name,
                    file,
                    retfile_extension,
                    bgtask,
                    **kwargs
                )
            except:
                raise HTTPException(status_code=503, detail="Error") 
            finally:
                # print("finally0")
                pass

    def post_processing(self, file_dst_path: str, **kwargs):

        ftype_dst = tools.check_filetype(file_dst_path)
        fname = os.path.basename(file_dst_path)
        ext = tools.get_file_extension(file_dst_path)
        return FileResponse(
            file_dst_path,
            filename=f"{fname}",
            media_type = f'video/{ext}'
            # background=bgtask
        )