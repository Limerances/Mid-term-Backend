from django.http import HttpResponse, StreamingHttpResponse, JsonResponse, HttpResponseNotFound
import subprocess
import json
import re
import ast
import os
import time
from pathlib import Path
from .ssh_pool import SSHConnectionPool
from urllib.parse import unquote
from Crypto.Cipher import AES
import base64
from Crypto.Util.Padding import unpad
import tempfile
import os
import mimetypes

TEMP_DIR = "tmp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# KEY_PATH = '/Users/apple/.ssh/id_rsa.pub'
KEY_PATH = '/Users/xzbw/.ssh/id_rsa.pub'
# KEY_PATH = '~/.ssh/id_rsa.pub'
SERVER_TH = 'yanghailong@192.168.10.21'

# pool_th = SSHConnectionPool(
#     hostname='192.168.10.21',
#     username='yanghailong',
#     key_filename=KEY_PATH,
#     port=22,
#     max_connections=5
# )

print(f"[SSHConnectionPool] 正在创建连接池... pool_th_yanghailong")
pool_th_yanghailong = SSHConnectionPool(
    hostname='192.168.10.21',
    username='yanghailong',
    key_filename=KEY_PATH,
    port=22,
    max_connections=5
)

print(f"[SSHConnectionPool] 正在创建连接池... pool_th_xjtu_cx")
pool_th_xjtu_cx = SSHConnectionPool(
    hostname='192.168.10.21',
    username='xjtu_cx',
    key_filename=KEY_PATH,
    port=22,
    max_connections=5
)

print(f"[SSHConnectionPool] 正在创建连接池... pool_th_penglin_lxx")
pool_th_penglin_lxx = SSHConnectionPool(
    hostname='192.168.10.21',
    username='penglin_lxx',
    key_filename=KEY_PATH,
    port=22,
    max_connections=5
)

print(f"[SSHConnectionPool] 正在创建连接池... pool_gpu7")
pool_gpu7 = SSHConnectionPool(
    hostname='10.254.46.25',
    username='huoda',
    key_filename=KEY_PATH,
    port=22,
    max_connections=5
)

print(f"[SSHConnectionPool] 正在创建连接池... pool_hg_buaa_hipo")
pool_hg_buaa_hipo = SSHConnectionPool(
    hostname='60.245.128.14',
    username='buaa_hipo',
    key_filename=KEY_PATH,
    port=65010,
    max_connections=5
)

print(f"[SSHConnectionPool] 正在创建连接池... pool_hg_dtune")
pool_hg_dtune = SSHConnectionPool(
    hostname='60.245.128.14',
    username='dtune',
    key_filename=KEY_PATH,
    port=65010,
    max_connections=5
)

print(f"[SSHConnectionPool] 正在创建连接池... pool_hg_wangxg")
pool_hg_wangxg = SSHConnectionPool(
    hostname='60.245.128.14',
    username='wangxg',
    key_filename=KEY_PATH,
    port=65010,
    max_connections=5
)

print(f"[SSHConnectionPool] 正在创建连接池... pool_hg_wangjh")
pool_hg_wangjh = SSHConnectionPool(
    hostname='60.245.128.14',
    username='wangjh',
    key_filename=KEY_PATH,
    port=65010,
    max_connections=5
)

def get_pool(pool_name):
    pool = None
    if pool_name == "pool_th_yanghailong":
        pool = pool_th_yanghailong
    elif pool_name == "pool_th_xjtu_cx":
        pool = pool_th_xjtu_cx
    elif pool_name == "pool_th_penglin_lxx":
        pool = pool_th_penglin_lxx
    elif pool_name == "pool_gpu7":
        pool = pool_gpu7
    elif pool_name == "pool_hg_buaa_hipo":
        pool = pool_hg_buaa_hipo
    elif pool_name == "pool_hg_dtune":
        pool = pool_hg_dtune
    elif pool_name == "pool_hg_wangxg":
        pool = pool_hg_wangxg
    elif pool_name == "pool_hg_wangjh":
        pool = pool_hg_wangjh
    else:
        raise ValueError(f"未知的连接池名称: {pool_name}")
    return pool

def decrypt_cmd(cmd):
    try:
        print(f"[decrypt_cmd] 收到加密命令: {cmd}")
        key = "wefhwuf284hvnien"
        iv  = "84fhwbsk109jzmlh"
        encrypted_bytes = base64.b64decode(cmd)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        decrypted = cipher.decrypt(encrypted_bytes)

        # 去除 PKCS7 padding
        pad_len = decrypted[-1]
        return decrypted[:-pad_len].decode('utf-8')

    except Exception as e:
        raise ValueError("解密失败")


def execute_ssh_command(pool, command):
    """使用连接池执行SSH命令"""
    client = None
    try:
        client = pool.get_connection()
        stdin, stdout, stderr = client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()
    finally:
        if client:
            pool.return_connection(client)
            
def execute_ssh_command_image(pool, command):
    """使用连接池执行SSH命令"""
    client = None
    try:
        client = pool.get_connection()
        stdin, stdout, stderr = client.exec_command(command)
        return stdout.read(), stderr.read()
    finally:
        if client:
            pool.return_connection(client)
            
def execute_ssh_command_text(pool, command):
    """使用连接池执行SSH命令"""
    client = None
    try:
        client = pool.get_connection()
        stdin, stdout, stderr = client.exec_command(command)
        return stdout.read(), stderr.read()
    finally:
        if client:
            pool.return_connection(client)

def stream_ssh_command(pool, command, slp=True):
    """使用连接池执行SSH命令并返回生成器"""
    client = None
    try:
        client = pool.get_connection()
        stdin, stdout, stderr = client.exec_command(command)
        
        while True:
            line = stdout.readline()
            if not line:
                if stdout.channel.exit_status_ready():
                    break
                continue
            
            yield f"data: {line.rstrip()}\n\n"
            if slp == True:
                time.sleep(0.001)
        
        yield "data: [done]\n\n"
    except Exception as e:
        yield f"data: [error] {str(e)}\n\n"
    finally:
        if client:
            pool.return_connection(client)

def check_path_exists(pool, pool_name, path):
    # print(f"checking path: {path}")
    stdout, stderr = execute_ssh_command(pool, f"ls {path}")
    print("path check stdout:", stdout)
    print("path check stderr:", stderr)
    # if(stderr.strip() != ""):
    #     raise ValueError(f"{pool_name} : {stderr}")
        # raise (f"{pool_name} : {stderr}")

def hello(request):
    print("debug: hello")
    return HttpResponse("Hello world ! ")


def test_api(request):
    check_path_exists(pool_th_yanghailong, "pool_th_yanghailong","/thfs3/home/yanghailong/midterm-demo/workdir/GZDW/misa-md")
    return JsonResponse({
        "errno": 0,
        "message": "API is working correctly"
    })


def excute(request,pool_name, cmd):
    try:
        pool = get_pool(pool_name)
        
        print("[excute] 收到请求")
        cmd = decrypt_cmd(cmd) # 解码URL编码的命令
        cmd = 'bash' + ' ' + cmd
        # cmd = 'bash /thfs3/home/yanghailong/midterm-demo/workdir/GZDW/misa-md/run_analysis.sh'
        print(f"[excute] 执行命令: {cmd}")
    
        response = StreamingHttpResponse(
            stream_ssh_command(pool, cmd),
            content_type='text/event-stream',
        )
        response['Cache-Control'] = 'no-cache'
        return response
        
    except Exception as e:
        print(f"[excute] 错误: {str(e)}")
        return JsonResponse(
            {"status": 500, "error": str(e)},
            status=500
        )


def get_image(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("[get_image] 收到请求数据:", data)
            
            path = data.get('path')
            pool_name = data.get('poolName')
            
            if not path or not pool_name:
                return JsonResponse({"errno": 1, "message": "缺少必要参数 path 或 poolName"}, status=400)
            
            pool = get_pool(pool_name)

            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False)
            temp_file_path = temp_file.name
            temp_file.close()

            # 使用本地 subprocess 执行 scp
            scp_cmd = [
                'scp',
                '-P', str(pool.port), 
                f'{pool.username}@{pool.hostname}:{path}',
                temp_file_path
            ]
            print("[get_image] 执行本地 scp 命令:", ' '.join(scp_cmd))

            try:
                subprocess.run(scp_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                os.remove(temp_file_path)
                return JsonResponse({
                    "errno": 1,
                    "message": f"SCP 失败: {e.stderr.decode('utf-8')}"
                }, status=500)
            print("1")
            
            # 读取本地临时文件内容
            try:
                with open(temp_file_path, 'rb') as f:
                    image_data = f.read()
            except Exception as e:
                os.remove(temp_file_path)
                return JsonResponse({
                    "errno": 1,
                    "message": f"读取本地临时文件失败: {str(e)}"
                }, status=500)

            # 获取 MIME 类型
            mime_type, _ = mimetypes.guess_type(temp_file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            content_type = mime_type.strip()
            
            os.remove(temp_file_path)

            return HttpResponse(image_data, content_type=content_type)

        except Exception as e:
            print(f"[get_image] 错误: {str(e)}")
            return JsonResponse({
                "errno": 1,
                "message": f"获取失败: {str(e)}"
            }, status=500)

    return JsonResponse({"errno": 1, "message": "请求方法不支持"}, status=405)


def get_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("[get_text] 收到请求数据:", data)
            
            path = data.get('path')
            pool_name = data.get('poolName')

            if not path or not pool_name:
                return JsonResponse({"errno": 1, "message": "缺少必要参数 path 或 poolName"}, status=400)

            pool = get_pool(pool_name)

            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False)
            temp_file_path = temp_file.name
            temp_file.close()

            # 使用 subprocess 执行 scp 命令
            scp_cmd = [
                'scp',
                '-P', str(pool.port),
                f'{pool.username}@{pool.hostname}:{path}',
                temp_file_path
            ]
            print("[get_text] 执行本地 scp 命令:", ' '.join(scp_cmd))

            try:
                subprocess.run(scp_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                print("[get_text] scp 失败:", e.stderr)
                os.remove(temp_file_path)
                return JsonResponse({
                    "errno": 1,
                    "message": f"SCP 失败: {e.stderr.decode('utf-8')}"
                }, status=500)

            # 读取文本内容
            try:
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except Exception as e:
                os.remove(temp_file_path)
                return JsonResponse({
                    "errno": 1,
                    "message": f"读取本地文件失败: {str(e)}"
                }, status=500)

            # 删除临时文件
            os.remove(temp_file_path)

            return JsonResponse({
                "errno": 0,
                "text": text,
                "message": "获取成功"
            })

        except Exception as e:
            print(f"[get_text] 错误: {str(e)}")
            return JsonResponse({
                "errno": 1,
                "message": f"获取失败: {str(e)}"
            }, status=500)

    return JsonResponse({"errno": 1, "message": "请求方法不支持"}, status=405)


def get_page_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            name = data.get('name')
    
            if not name:
                return JsonResponse({"errno": 1, "message": "缺少必要参数 name"}, status=400)
            
            path = "pageinfo/" + name + ".json"
            
            with open(path, 'r') as f:
                info = json.load(f)
            if not info:
                return JsonResponse({"errno": 1, "message": "页面信息为空"}, status=404)

            return JsonResponse({"errno": 0, "info": info, "message": "获取成功"})
            
        except Exception as e:
            print(f"[get_page_info] 错误: {str(e)}")
            return JsonResponse({
                "errno": 1,
                "message": f"获取失败: {str(e)}"
            }, status=500)
    
    return JsonResponse({"errno": 1, "message": "请求方法不支持"}, status=405)



# SERVER84 = 'jinjm@192.168.165.231'
# SERVER86 = 'jinjm@192.168.165.232'

# # 创建SSH连接池
# pool84 = SSHConnectionPool(
#     hostname='192.168.165.231',
#     username='jinjm',
#     key_filename=KEY_PATH,
#     port=22222,
#     max_connections=5
# )

# pool86 = SSHConnectionPool(
#     hostname='192.168.165.232',
#     username='jinjm',
#     key_filename=KEY_PATH,
#     port=22222,
#     max_connections=5
# )




# """
# algo参数：kclique, pagerank, gcn
# dataset参数：rmat16, rmat17, rmat18, rmat19, rmat20
# """
# def part1(request, algo, dataset):
#     print(f'[part1_execute] 请求算法：{algo} 数据集: {dataset}')

#     cmd = f'/usr/bin/python3 -u /home/jinjm/local/cmd/run_part1.py --algo {algo} --dataset {dataset}'
#     print(f'[part1_execute] 执行命令: {cmd}')
    
#     try:
#         response = StreamingHttpResponse(
#             stream_ssh_command(pool84, cmd),
#             content_type='text/event-stream',
#         )
#         response['Cache-Control'] = 'no-cache'
#         return response
        
#     except Exception as e:
#         print(f'[part1_execute] 错误: {str(e)}')
#         return JsonResponse(
#             {"status": 500, "error": str(e)},
#             status=500
#         )


# def get_part1_result(request, algo, dataset):
#     """获取part1执行结果"""
#     print('[get_part1_result] 请求结果')
    
#     result_file = f'/home/jinjm/local/result_{algo}_{dataset}.json'
#     cmd = f'cat {result_file}'
    
#     try:
#         print(f'[get_part1_result] 获取结果: {cmd}')
#         stdout, stderr = execute_ssh_command(pool84, cmd)
        
#         if stderr:
#             return JsonResponse(
#                 {"status": 500, "error": "获取结果失败", "details": stderr},
#                 status=500
#             )
        
#         return JsonResponse(json.loads(stdout))
        
#     except json.JSONDecodeError:
#         print('[get_part1_result] JSON解析失败')
#         return JsonResponse(
#             {"status": 500, "error": "结果格式无效"},
#             status=500
#         )
#     except Exception as e:
#         print(f'[get_part1_result] 未知错误: {str(e)}')
#         return JsonResponse(
#             {"status": 500, "error": str(e)},
#             status=500
#         )



# # CACHE_DIR = Path("/home/jasper/part3_cache")
# # CACHE_DIR.mkdir(exist_ok=True, parents=True)

# # def get_cache_path(framework, algo):
# #     """获取缓存文件路径"""
# #     return CACHE_DIR / f"{framework}_{algo}.json"


# # 获取当前项目根目录（假设 part3_cache 和 backend 同级）
# PROJECT_ROOT = Path(__file__).parent.parent  # backend -> 项目根目录
# CACHE_DIR = PROJECT_ROOT / "part3_cache"
# CACHE_DIR.mkdir(exist_ok=True, parents=True)

# def get_cache_path(framework, algo):
#     """获取缓存文件路径"""
#     return CACHE_DIR / f"{framework}_{algo}.json"



# def part3_cgafile(request, framework, algo, rw):
#     print("[part3_cgafile] 收到请求")
#     cmd = f'/home/jinjm/anaconda3/bin/python -u /home/jinjm/local/run_part3.py --fw fw1 --op readfile --algorithm {algo}'
#     print("执行命令:", cmd)

#     try:
#         stdout, stderr = execute_ssh_command(pool86, cmd)
        
#         if stderr:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': '命令执行失败',
#                 'error': stderr,
#                 'command': cmd
#             }, status=500)
        
#         output_lines = stdout.splitlines()
        
#         return JsonResponse({
#             'status': 'success',
#             'framework': framework,
#             'algorithm': algo,
#             'operation': 'readfile',
#             'content': output_lines,
#             'command': cmd
#         })

#     except Exception as e:
#         return JsonResponse({
#             'status': 'error',
#             'message': '执行过程中发生异常',
#             'error': str(e),
#             'command': cmd
#         }, status=500)



# def part3_3(request, framework, algo):
#     cmd = f'/home/jinjm/anaconda3/bin/python -u /home/jinjm/local/run_graph_computing.py --fw {framework} --"data" {algo}'
#     try:
#         response = StreamingHttpResponse(
#             stream_ssh_command(pool86, cmd),
#             content_type='text/event-stream',
#         )
#         response['Cache-Control'] = 'no-cache'
#         return response
        
#     except Exception as e:
#         print(f"[part3] 响应创建失败: {str(e)}")
#         return JsonResponse(
#             {"status": 500, "error": str(e)},
#             status=500
#         )



# def part3(request, framework, algo, dataset):
#     print("[part3] 收到请求")
#     if framework == "1":
#         cmd = f"/home/jinjm/anaconda3/bin/python -u /home/jinjm/local/run_part3.py --fw fw1 --op run --algorithm {algo} --dataset {dataset}"
#     elif framework == "2":
#         cmd = f"/home/jinjm/anaconda3/bin/python -u /home/jinjm/local/run_part3.py --fw fw2 --op run --algorithm {algo} --dataset {dataset}"
#     elif framework == "3":
#         cmd = f'/home/jinjm/anaconda3/bin/python -u /home/jinjm/local/run_graph_computing.py --fw {framework} --"data" {algo}'    
#     print("执行命令:", cmd)
    
#     try:
#         response = StreamingHttpResponse(
#             stream_ssh_command(pool86, cmd),
#             content_type='text/event-stream',
#         )
#         response['Cache-Control'] = 'no-cache'
#         return response
        
#     except Exception as e:
#         print(f"[part3] 响应创建失败: {str(e)}")
#         return JsonResponse(
#             {"status": 500, "error": str(e)},
#             status=500
#         )


# def get_part3_result(request, framework, algo):
#     """
#     获取已缓存的JSON结果
#     """
#     print(f"[get_part3_result] 获取结果: {framework}/{algo}")
    
#     try:
#         cmd = "cat /home/jinjm/local/result.json"
#         stdout, stderr = execute_ssh_command(pool86, cmd)
        
#         if stderr:
#             return JsonResponse(
#                 {"status": 500, "error": stderr},
#                 status=500
#             )
        
#         json_data = json.loads(stdout)
        
#         # 缓存到本地文件
#         cache_file = get_cache_path(framework, algo)
#         with open(cache_file, 'w') as f:
#             json.dump(json_data, f, indent=2)
#         print(f"[get_part3_result] JSON结果已缓存到 {cache_file}")
        
#         return JsonResponse(json_data)
        
#     except json.JSONDecodeError:
#         print("[get_part3_result] JSON解析错误")
#         return JsonResponse(
#             {"status": 500, "error": "无效的JSON格式"},
#             status=500
#         )
#     except Exception as e:
#         print(f"[get_part3_result] 未知错误: {str(e)}")
#         return JsonResponse(
#             {"status": 500, "error": str(e)},
#             status=500
#         )


# def part3data(request, framework, algo, data_type):
#     """获取缓存数据中的特定字段"""
#     print(f"[part3data] 请求数据: {framework}/{algo}/{data_type}")
    
#     try:
#         # 1. 检查缓存文件是否存在
#         cache_file = get_cache_path(framework, algo)
#         if not os.path.exists(cache_file):
#             return JsonResponse(
#                 {"status": 404, "error": "缓存文件不存在，请先执行part3接口"},
#                 status=404
#             )
        
#         # 2. 读取缓存文件
#         with open(cache_file, 'r') as f:
#             cached_data = json.load(f)
        
#         # 4. 检查请求的数据是否存在
#         if "data" not in cached_data or data_type not in cached_data["data"]:
#             return JsonResponse(
#                 {"status": 404, "error": f"请求的数据类型 '{data_type}' 不存在于结果中"},
#                 status=404
#             )
        
#         # 5. 返回请求的数据
#         return JsonResponse({
#             "status": 200,
#             "framework": framework,
#             "algorithm": algo,
#             "data_type": data_type,
#             "data": cached_data["data"][data_type]
#         })
        
#     except json.JSONDecodeError:
#         return JsonResponse(
#             {"status": 500, "error": "缓存文件格式错误"},
#             status=500
#         )
#     except Exception as e:
#         return JsonResponse(
#             {"status": 500, "error": f"服务器错误: {str(e)}"},
#             status=500
#         )


# def part3_moni(request, framework, algo, dataset):
#     print("[part3] 收到请求")
    
#     cmd = f"/home/jinjm/anaconda3/bin/python -u /home/jinjm/local/run_part3.py --fw fw1 --op runsim --algorithm {algo} --dataset {dataset}"
#     # cmd = f'bash /home/jinjm/local/run_graph_1.sh {algo}'
#     print("执行命令:", cmd)
    
#     try:
#         response = StreamingHttpResponse(
#             stream_ssh_command(pool86, cmd, slp=False),
#             content_type='text/event-stream',
#         )
#         response['Cache-Control'] = 'no-cache'
#         return response
        
#     except Exception as e:
#         print(f"[part3] 响应创建失败: {str(e)}")
#         return JsonResponse(
#             {"status": 500, "error": str(e)},
#             status=500
#         )



# def part3_moni2(request, algo, dataset):
#     print("[part3] 收到请求")
#     cmd = f"/home/jinjm/anaconda3/bin/python -u /home/jinjm/local/run_part3.py --fw fw2 --op runsim --algorithm {algo} --dataset {dataset}"
#     print("执行命令:", cmd)
    
#     try:
#         response = StreamingHttpResponse(
#             stream_ssh_command(pool86, cmd, slp=False),
#             content_type='text/event-stream',
#         )
#         response['Cache-Control'] = 'no-cache'
#         return response
        
#     except Exception as e:
#         print(f"[part3] 响应创建失败: {str(e)}")
#         return JsonResponse(
#             {"status": 500, "error": str(e)},
#             status=500
#         )



# def stream_test(request):
#     print("[stream_test] 收到SSE请求")
#     try:
#         cmd = 'bash /home/jinjm/local/cmd/run_stream.sh'
#         response = StreamingHttpResponse(
#             stream_ssh_command(pool84, cmd),
#             content_type='text/event-stream',
#         )
#         response['Cache-Control'] = 'no-cache'
#         print("[stream_test] 流式响应准备就绪")
#         return response
#     except Exception as e:
#         print(f"[stream_test] 响应创建失败: {str(e)}")
#         raise


# def read_log_file(request, filename):
#     # 获取当前文件（views.py）的绝对路径目录（backend目录）
#     current_dir = os.path.dirname(os.path.abspath(__file__))
    
#     # 构建相对路径：backend -> 项目根目录 -> logfile -> 目标文件
#     log_file_path = os.path.normpath(os.path.join(current_dir, '..', 'logfile', f"{filename}.log"))
        
#     # 检查文件是否存在
#     if not os.path.exists(log_file_path):
#         return HttpResponseNotFound(f"Log file {filename}.log not found")
    
#     # 检查是否为合法文件（防止目录遍历攻击）
#     if not os.path.isfile(log_file_path):
#         return HttpResponse("Invalid file path", status=400)
    
#     try:
#         # 读取文件内容
#         with open(log_file_path, 'r') as f:
#             content = f.read()
        
#         # 返回文件内容
#         return HttpResponse(content, content_type='text/plain')
    
#     except Exception as e:
#         # 处理读取错误
#         return HttpResponse(f"Error reading file: {str(e)}", status=500)