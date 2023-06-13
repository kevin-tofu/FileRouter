
# filerouter  

## What this repository is going to solve

This library provides functions for routing media such as images and videos via FastAPI.

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
```
