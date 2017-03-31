# reqeust format

[TOC]

## from client to master

1.**add task**
　　api: /master/add_job?token=xxxx

- request:
```
{
    type:0,  # 0: request, 1: response
    job: {
        src_filename = "record.bin"
        dst_dir = "/tmp/"
        dst_format = "flv"
        segments:1-5:2-10
    }
}
```
- response:
```
{
    type:1,
    err_code:0, # 0: ok, < 0: failure
    err_msg:"ok"
}
```
- example:
```
{
    "type":0,
    "job": {
        "src_filename": "record.bin",
        "dst_dir": "/tmp/",
        "dst_format": "flv",
        "segments":"1-5:2-10"
    }
}
```

2.**get state of specified job**
　　*api:/master/get_job?token=xxxx*
- request:
```
{
        type: 0
        task_id: ""
}
```
- response:
```
{
    type:1,  
    err_code:0, # 0: ok, < 0: failure
    err_msg:"ok"
    job: {
        id:xxx
        state:0
        srt_path:""
        dst_path:""
        progress:35
    }
}
```
- example:
```
{
    "type":0,
    "job_id":"1490776760.13"
}
```

3.**get jobs**
　　api:/master/get_jobs?token=xxxx
- request:
```
{
    type:0, # 0: request, 1: response
    start_index: 0,
    limit: 10
    sortby:time
}
```

- response:
```
{
    type:1, # 0: request, 1: response
    err_code: 0,
    err_msg: "ok"
    start_index: 0,
    num_jobs: 10
    jobs:[
        {
            id:
            state:
            srt_path:
            dst_path:
            progress:
        }
        ......
    ]
}
```
- example:
```
{
        "type": 0
        "start_index": 0,
    	"limit": 10
    	"sortby":"time"
}
```
------

## from worker to master
１.**register worker**
　　api:/master/register_worker?token=xxxx
- request:
```
{
    type: 0
    ip: ip
    port: port
    state:0 # 0:idle ; 1: busy
}
```

- response:
```
{
    type:1
    error_code:0
    worker_id: xxx
}
```
- example:
```
{
    "type":0,
    "ip":"0.0.0.0",
    "port":20001,
    "state":0
}
```

2.**heartbeat**
　　api:/master/worker_heartbeat?token=xxxx
- request:
```
{
    type:0
    worker_id: id
    worker_state: 0
}
```

- response:
```
{
    type:1
    error_code:0
}
```
- example:
```
{
    "type":0
    "worker_id": "id"
    "worker_state": 0
}```



------
## from master to worker

1. **add task**

- request:
```
{
    type: 0
    task:{
        id = ""
        src_filename = ""
        src_file_id = "" 
        dst_dir = ""
        dst_format = ""
        map_filename = ""
        map_file_id = ""
    }
}
```
- response:
```
{
    type:1
    error_code:0
}
```
- example:
```
{
    "type": 0,
    "task":{
        "id" = "",
        "src_filename" = ""
        "src_file_id" = "" 
        "dst_dir" = ""
        "dst_format" = ""
        "map_filename" = ""
        "map_file_id" = ""
    }
}
```
------
2.  **get task information**
- request:
```
{
        type: 0
        task_id: ""
}
```
- response:
```
{
    type:1
    error_code:0 
    task: {
        id = "",
        state = 0,
        result = 0
        progress = 0,
    }
}

```
- example:
```
{
    "type":1
    "error_code":0,
    "task": {
        "id" = "",
        "state" = 0,
        "result" = 0,
        "progress" = 0
    }
}
```
------
3. cancel task
- request:
```
{
        type: 0
        task_id: ""
}
```
- response:
```
{
    type:1
    error_code:0 
}

```
- example:
```
{
        "type": 0
        "task_id": ""
}
```






