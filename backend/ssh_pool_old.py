import paramiko
from queue import Queue
import threading
import time

class SSHConnectionPool:
    def __init__(self, hostname, username, password=None, key_filename=None, port=22, max_connections=5):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        
        # 初始化连接池
        for _ in range(max_connections):
            self._create_connection()
    
    def _create_connection(self):
        """创建新的SSH连接"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                key_filename=self.key_filename,
                port=self.port
            )
            self.pool.put(client)
        except Exception as e:
            print(f"创建SSH连接失败: {str(e)}")
    
    def get_connection(self):
        """从连接池获取一个连接"""
        try:
            client = self.pool.get(timeout=5)
            if not self._is_connection_alive(client):
                client.close()
                with self.lock:
                    self._create_connection()
                client = self.pool.get(timeout=5)
            return client
        except Exception as e:
            print(f"获取SSH连接失败: {str(e)}")
            return None
    
    def return_connection(self, client):
        """将连接返回池中"""
        if client and self._is_connection_alive(client):
            self.pool.put(client)
        else:
            with self.lock:
                self._create_connection()
    
    def _is_connection_alive(self, client):
        """检查连接是否仍然有效"""
        try:
            client.exec_command('echo "test"', timeout=1)
            return True
        except:
            return False
    
    def close_all(self):
        """关闭所有连接"""
        while not self.pool.empty():
            try:
                client = self.pool.get_nowait()
                client.close()
            except:
                pass

# 使用示例
"""
# 创建连接池
pool = SSHConnectionPool(
    hostname='your_host',
    username='your_username',
    password='your_password',  # 或者使用 key_filename
    max_connections=5
)

# 使用连接
try:
    client = pool.get_connection()
    stdin, stdout, stderr = client.exec_command('your_command')
    result = stdout.read().decode()
    print(result)
finally:
    pool.return_connection(client)

# 程序结束时关闭所有连接
pool.close_all()
""" 