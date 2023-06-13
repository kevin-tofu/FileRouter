
import os
from typing import List, Optional
import zipfile

# from fastapi.responses import FileResponse, JSONResponse
from fastapi import HTTPException, BackgroundTasks
from fastapi import Response, UploadFile
# import numpy as np
import io

from filerouter import tools
from filerouter.logconf import medialogger
logger = medialogger(__name__)
print('__name__', __name__)

class config():
    def __init__(self, **kwargs):

        print("kwargs: ", kwargs)
        self.path_data = kwargs["path_data"] if "path_data" in kwargs.keys() else "./temp"


class processor():

    def __init__(self, **kwargs):
        pass
    
    async def process_files(
        self,
        process_name: str,
        fpath_files: List[str],
        fpath_dst: Optional[str] = None,
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):
        raise NotImplementedError()

    async def process_file(
        self,
        process_name: str,
        fpath_org: str,
        fpath_dst: Optional[str] = None,
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):
        raise NotImplementedError()
    
    async def process_bytes(
        self,
        process_name :str,
        data: dict,
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):
        raise NotImplementedError()

    async def process_bytes_list(
        self,
        process_name :str,
        data_list: list[dict],
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):
        raise NotImplementedError()


class router():
    def __init__(
        self,
        processor: processor,
        config: config
    ):

        self.processor = processor
        self.config = config
        self.path_data = config.path_data
        os.makedirs(self.path_data, exist_ok=True)


    async def _files_post(
        self,
        process_name: str,
        files_list: List[UploadFile],
        retfile_extension: Optional[str] = None,
        bgtask: BackgroundTasks = BackgroundTasks(),
        **kwargs
    ):
        kwargs['bgtask'] = bgtask
        test = kwargs['test']
        time_sleep = kwargs['time_sleep'] if 'time_sleep' in kwargs.keys() else 10

        path_files_list = list()
        fname_list = list()
        fname_org_list = list()
        for file in files_list:

            logger.info(f'{file.filename}, {file.content_type}')

            fname_org = file.filename
            fname, uuid_f = tools.fname2uuid(fname_org)
            tools.save_file(self.path_data, fname, file, test)

            fname_list.append(fname)
            path_files_list.append(f"{self.path_data}/{fname}")
            fname_org_list.append(fname_org)
        
        kwargs["fname_org_list"] = fname_org_list
        bgtask.add_task(tools.remove_files, path_files_list, time_sleep)

        if retfile_extension is not None:
            fname_dst = tools.make_fname_uuid(retfile_extension)
            fpath_dst = f"{self.path_data}/{fname_dst}"
            bgtask.add_task(tools.remove_file, fpath_dst, time_sleep)
        else:
            fpath_dst = None

        result = await self.processor.process_files(
            process_name,
            path_files_list,
            fpath_dst,
            **kwargs
        )
        
        if type(fpath_dst) is str:
            if os.path.exists(fpath_dst):
                return self.post_processing(fpath_dst, **kwargs)
            else:
                return result
        else:
            return result
    
    
    async def files_post(
        self,
        process_name: str,
        files_list: List[UploadFile],
        retfile_extension: Optional[str] = None,
        bgtask: BackgroundTasks = BackgroundTasks(),
        **kwargs
    ):

        logger.info("files_post")
        test = kwargs['test']
        
        if test == 1:
            kwargs['time_sleep'] = 5
            return await self._files_post(process_name, files_list, retfile_extension, bgtask, **kwargs)

        else:
            try:
                return await self._files_post(process_name, files_list, retfile_extension, bgtask, **kwargs)
            except:
                raise HTTPException(status_code=503, detail="Error") 
            finally:
                # print("finally0")
                pass
            
        
    def zip_extractall(self, bgtask, file_name: str, time_sleep: int):
        path_dir_export = f"{self.path_data}/{os.path.splitext(file_name)[0]}"
        os.makedirs(path_dir_export)
        bgtask.add_task(tools.remove_dir, path_dir_export, time_sleep)
        with zipfile.ZipFile(f"{self.path_data}/{file_name}") as zf:
            zf.extractall(path=path_dir_export)
        bgtask.add_task(tools.remove_dir, path_dir_export, time_sleep)

    
    async def _post_file(
        self,
        process_name: str,
        file: UploadFile,
        retfile_extension: Optional[str] = None,
        bgtask: BackgroundTasks = BackgroundTasks(),
        **kwargs
    ):
        test = kwargs["test"]
        fname_org = file.filename
        ftype_input = tools.check_filetype(fname_org)
        fname, uuid_f = tools.fname2uuid(fname_org)
        tools.save_file(self.path_data, fname, file, test)
        kwargs["fname_org"] = fname_org

        time_sleep = kwargs['time_sleep'] if 'time_sleep' in kwargs.keys() else 10

        
        if ftype_input == tools.FileType.ZIP:
            self.zip_extractall(bgtask, fname, time_sleep)
            
        if retfile_extension is not None:
            fname_dst = tools.addstr2fname(fname, "-res", ext = retfile_extension)
            fpath_dst = f"{self.path_data}/{fname_dst}"
            bgtask.add_task(tools.remove_file, fpath_dst, time_sleep)
        else:
            fpath_dst = None

        result = await self.processor.process_file(
            process_name,
            f"{self.path_data}/{fname}",
            fpath_dst,
            bgtask,
            **kwargs
        )
        bgtask.add_task(tools.remove_file, f"{self.path_data}/{fname}", time_sleep)
        
        return result
        
    async def file_post(
        self,
        process_name: str,
        file: UploadFile,
        retfile_extension: Optional[str] = None,
        bgtask: BackgroundTasks = BackgroundTasks(),
        **kwargs
    ):

        logger.info("file_post")
        
        if kwargs["test"] == 1:
            kwargs['time_sleep'] = 5
            return await self._post_file(process_name, file, retfile_extension, bgtask, **kwargs)

        else:
            try:
                return await self._post_file(process_name, file, retfile_extension, bgtask, **kwargs)
            except:
                raise HTTPException(status_code=503, detail="Error") 
            finally:
                # print("finally0")
                pass
        
    
    async def _file_post_BytesIO(
        self,
        process_name: str,
        file: UploadFile,
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):
        fname_org = file.filename
        file_byte = io.BytesIO(await file.read())

        info = dict(
            filename=fname_org,
            bytesio=file_byte
        )
        return await self.processor.process_bytes(
            process_name,
            info,
            bgtask,
            **kwargs
        )
        

    async def file_post_BytesIO(
        self,
        process_name: str,
        file: UploadFile,
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):

        logger.info("file_post_BytesIO")

        if kwargs['test'] == 1:
            return self._file_post_BytesIO(process_name, process_name, file, bgtask, **kwargs)
        else:
            try:
                return self._file_post_BytesIO(process_name, process_name, file, bgtask, **kwargs)
            except:
                raise HTTPException(status_code=503, detail="Error") 
            finally:
                # print("finally0")
                pass

    
    async def _files_post_BytesIO(
        self,
        process_name: str,
        files: List[UploadFile],
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):
        files_list = list()
        for file in files:
            fname_org = file.filename
            file_byte = io.BytesIO(await file.read())
            files_list.append(
                dict(
                    filename=fname_org,
                    bytesio=file_byte
                )
            )

        result = await self.processor.process_bytes_list(
            process_name,
            files_list,
            bgtask,
            **kwargs
        )
        return result

    async def files_post_BytesIO(
        self,
        process_name: str,
        files: List[UploadFile],
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):

        logger.info("files_post_BytesIO")
        
        test = kwargs["test"]
        if test == 1:
            
            return await self._files_post_BytesIO(process_name, files, bgtask, **kwargs)
        else:
            try:
                return await self._files_post_BytesIO(process_name, files, bgtask, **kwargs)
                
            except:
                raise HTTPException(status_code=503, detail="Error") 
            finally:
                # print("finally0")
                pass
                