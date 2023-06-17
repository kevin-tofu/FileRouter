import os, sys

import io
from fastapi import APIRouter, File, UploadFile, Header, Depends
from fastapi import BackgroundTasks
# from fastapi import Response
from typing import Optional
import glob

import filerouter
from filerouter import processType

class myProcessor(filerouter.processor):
    def __init__(self):
        super().__init__()

    async def post_file_process(
        self,
        process_name: str,
        data: dict,
        file_dst_path: Optional[str] = None,
        bgtask: BackgroundTasks=BackgroundTasks(),
        **kwargs
    ):
        print(process_name)
        if process_name == 'files':
            ret = list()
            for d in data['file']:
                ret.append(os.path.basename(d['path']))
            return dict(status = "OK", fnamelist=ret)
        
        elif process_name == 'zip':
            zipped_file_path_extact = os.path.splitext(data['file']['path'])[0]
            print('zipped_file_path_extact:', zipped_file_path_extact)
            zippedFile_list = list()
            for file_path in glob.glob(f"{zipped_file_path_extact}/*"):
                print(file_path)
                zippedFile_list.append(file_path)

            return dict(status = "ok", zippedFiles=zippedFile_list)
        elif process_name == 'file-bytesio':
            
            return dict(
                filename=data['name'],
                sentence=data["bytesio"].getvalue().decode('utf-8')
            )
        
        elif process_name == 'files-bytesio':
            ret = list()
            for dloop in data['file']:
                # data['bytesio'] # 
                ret.append(
                    dict(
                        filename=dloop['name'],
                        sentence=dloop["bytesio"].getvalue().decode('utf-8')
                    )
                )
            return dict(info=ret)
        
        else:
            raise ValueError('')
            

    
test_config = dict(
    PATH_DATA = "./temp"
)

handler = filerouter.router(myProcessor(), filerouter.config(**test_config))
test_router = APIRouter(prefix="")


@test_router.post('/zip')
async def zip(
    file: UploadFile = File(...),
    bgtask: BackgroundTasks = BackgroundTasks(),
    test: Optional[int] = 0
):
    """
    """
    params = dict(
        test = test
    )
    return await handler.post_file(
        "zip", 
        processType.FILE,
        file,
        None,
        bgtask,
        **params
    )


@test_router.post('/files')
async def files(
    files: list[UploadFile],
    bgtask: BackgroundTasks = BackgroundTasks(),
    test: Optional[int] = 0
):
    """
    """
    params = dict(
        test = test
    )
    # print(params)

    return await handler.post_file(
        "files",
        processType.FILE,
        files,
        None,
        bgtask,
        **params
    )


@test_router.post('/files-bytesio')
async def files(
    files: list[UploadFile],
    test: Optional[int] = 0
):
    """
    """
    params = dict(
        test = test
    )
    # print(params)

    return await handler.post_file(
        "files-bytesio", 
        processType.BYTESIO,
        files,
        **params
    )

