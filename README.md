
# filerouter  

## What this repository is going to resolve

This library provides functions for routing files such as text, images and zip via FastAPI.

## How to install

### via poetry

```bash
poetry add git+https://github.com/kevin-tofu/FileRouter.git
```

## How to test this module

```bash

poetry run python3 test/test_server.py

```

## Usage Example

What you need to do is,  
  1. to define 'post_file_process' on inherited class from filerouter.processor
  2. to call post_file on endpoints

### 1. define 'post_file_process' on inherited
 class from filerouter.processor

```python

import filerouter
class myProcessor(filerouter.processor):
    def __init__(self):
        super().__init__()

    async def post_file_process(
        self,
        process_name: str,
        data: filerouter.fileInfo | list[filerouter.fileInfo],
        file_dst_path: Optional[str] = None,
        bgtask: BackgroundTasks=BackgroundTasks(),
        **kwargs
    ):
        print(process_name)
        if process_name == 'files':
            ret = list()
            for d in data:
                ret.append(os.path.basename(d.path))
            return dict(status = "OK", fnamelist=ret)

handler = filerouter.router(myProcessor(), filerouter.config())
```

 The definition of filerouter.fileInfo is below.
If your instruction is routing file or files by 'BYTES.IO', data (or list of data) has Bytes.io on the key 'bytesio'. But if your instruction is routing file or files by 'FILE', data has path for the file that clients post. Note that path of file (or files) is automatically going to be removed after response to clients by background process.  

```Python
class fileInfo():
    path: Optional[str]=None
    name: Optional[str]=None
    bytesio: Optional[io.BytesIO]=None
```

Here shows how to make instruction for routing.  
Your instruction is going to be done by calling post_file method with arguments.
This table shows the  arguments for the method.

| Arguments | Type | Description |
| --- | --- | --- | --- |
| process_name | str | Process name to distinguish what process it is. |
| process_type | filerouter.processType | which process type is choosed to route file, processType.FILE or processType.BYTESIO. |
| retfile_extension | str | - | File extention that is used for response file. FileRouter is going to create file automatically and pass the path of file to your post_file_process function. |
| bgtask | BackgroundTasks | - | Background task |

| **kwargs | dict | - | kwargs to be routed to your function for flexibility. |

### 2. to call post_file on endpoint

```python

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
    return await handler.post_file(
        "files",
        processType.FILE,
        files,
        None,
        bgtask,
        **params
    )
```
