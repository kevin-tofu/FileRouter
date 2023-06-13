import os, sys

import io
from fastapi import APIRouter, File, UploadFile, Header, Depends
from fastapi import BackgroundTasks
from fastapi import Response
from typing import List, Optional
import glob

# print(f"{os.pardir}/filerouter")
# sys.path.append(f"{os.pardir}/filerouter/")
# print(sys.path)

import filerouter


class myProcessor(filerouter.processor):
    def __init__(self):
        super().__init__()

    async def process_files(
        self,
        process_name: str,
        fpath_files: List[str],
        fpath_dst: Optional[str] = None,
        **kwargs
    ) -> dict:
        # if process_name == "files":
        return dict(status = "OK")


    async def process_file(
        self,
        process_name: str,
        fpath_org: str,
        fpath_dst: Optional[str] = None,
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):
        # print(fpath_org)
        zipped_file_path_extact = os.path.splitext(fpath_org)[0]
        print('zipped_file_path_extact:', zipped_file_path_extact)
        zippedFile_list = list()
        for file_path in glob.glob(f"{zipped_file_path_extact}/*"):
            print(file_path)
            zippedFile_list.append(file_path)

        return dict(status = "ok", zippedFiles=zippedFile_list)


    async def process_bytes(
        self,
        process_name :str,
        data: dict,
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):

        # do stuff
        return dict(
            filename=data['filename'],
            sentence=data["bytesio"].getvalue().decode('utf-8')
        )

    async def process_bytes_list(
        self,
        process_name :str,
        data_list: list[dict],
        bgtask: Optional[BackgroundTasks] = None,
        **kwargs
    ):
        ret = list()
        for data in data_list:
            # data['bytesio'] # 
            ret.append(
                dict(
                    filename=data['filename'],
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
    return await handler.file_post("zip", file, None, bgtask, **params)


@test_router.post('/files')
async def files(
    files: List[UploadFile],
    bgtask: BackgroundTasks = BackgroundTasks(),
    test: Optional[int] = 0
):
    """
    """
    params = dict(
        test = test
    )
    # print(params)

    return await handler.files_post("files", files, "json", bgtask, **params)


@test_router.post('/files-bytesio')
async def files(
    files: List[UploadFile],
    test: Optional[int] = 0
):
    """
    """
    params = dict(
        test = test
    )
    # print(params)

    # return await handler.file_posts("files", files, "json", bgtask, **params)
    return await handler.files_post_BytesIO("files", files, **params)

