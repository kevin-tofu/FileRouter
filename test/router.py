import os, sys

import io
from fastapi import APIRouter, File, UploadFile, Header, Depends
from fastapi import BackgroundTasks
# from fastapi import Response
from typing import Optional
import glob

import filerouter


class myProcessor(filerouter.processor):
    def __init__(self):
        super().__init__()

    async def post_files_process(
        self,
        process_name: str,
        files_org_info: list[dict],
        file_dst_path: Optional[str] = None,
        bgtask: BackgroundTasks=BackgroundTasks(),
        **kwargs
    ):
        return dict(status = "OK")


    async def post_file_process(
        self,
        process_name: str,
        file_org_info: list[dict],
        file_dst_path: Optional[str] = None,
        bgtask: BackgroundTasks=BackgroundTasks(),
        **kwargs
    ):
        # print(fpath_org)
        zipped_file_path_extact = os.path.splitext(file_org_info['path'])[0]
        print('zipped_file_path_extact:', zipped_file_path_extact)
        zippedFile_list = list()
        for file_path in glob.glob(f"{zipped_file_path_extact}/*"):
            print(file_path)
            zippedFile_list.append(file_path)

        return dict(status = "ok", zippedFiles=zippedFile_list)


    async def post_BytesIO_process(
        self,
        process_name: str,
        file_org_info: dict,
        file_dst_path: Optional[str] = None,
        bgtask: BackgroundTasks=BackgroundTasks(),
        **kwargs
    ):

        # do stuff
        return dict(
            filename=file_org_info['name'],
            sentence=file_org_info["bytesio"].getvalue().decode('utf-8')
        )

    async def post_ListBytesIO_process(
        self,
        process_name: str,
        files_org_info: list[dict],
        file_dst_path: Optional[str] = None,
        bgtask: BackgroundTasks=BackgroundTasks(),
        **kwargs
    ):
        ret = list()
        for data in files_org_info:
            # data['bytesio'] # 
            ret.append(
                dict(
                    filename=data['name'],
                    sentence=data["bytesio"].getvalue().decode('utf-8')
                )
            )

        return dict(info=ret)



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
        "zip", file, None, bgtask, **params
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

    return await handler.post_files("files", files, None, bgtask, **params)


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

    return await handler.post_files_BytesIO(
        "files", files, **params
    )

