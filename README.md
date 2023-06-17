
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


handler = filerouter.router(myProcessor(), filerouter.config())

```
