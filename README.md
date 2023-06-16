
# filerouter  

## What this repository is going to resolve

This library provides functions for routing files such as text and zip via FastAPI.

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

```python
handler = filerouter.router(myprocessor(), filerouter.config(**test_config))
```

```python

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
            ret.append(
                dict(
                    filename=data['name'],
                    sentence=data["bytesio"].getvalue().decode('utf-8')
                )
            )

        return dict(info=ret)


handler = filerouter.router(myProcessor(), filerouter.config())

```
