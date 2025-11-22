import threading
import traceback
import queue
import os
import torch
import sys
import datetime
import argparse

import threading
import queue
import websockets.exceptions
import websockets.sync.server
import bson
import time

import storage
import wrapper
import utils
import download_manager

import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

import random

DEFAULT_PASSWORD = "qDiffusion"
FRAGMENT_SIZE = 1048576
UPLOAD_IDS = {}

def log_traceback(label):
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    with open("crash.log", "a", encoding='utf-8') as f:
        f.write(f"{label} {datetime.datetime.now()}\n{tb}\n")
    print(label, tb)
    return tb

def get_scheme(password):
    password = password.encode("utf8")
    h = hashes.Hash(hashes.SHA256())
    h.update(password)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=h.finalize()[:16],
        iterations=480000,
    )
    return AESGCM(kdf.derive(password))

def encrypt(scheme, data):
    if scheme:
        nonce = secrets.token_bytes(16)
        data = nonce + scheme.encrypt(nonce, data, b"")
    return data

def decrypt(scheme, data):
    if scheme:
        data = scheme.decrypt(data[:16], data[16:], b"")
    return data

def get_id():
    return random.SystemRandom().randint(1, 2**31 - 1)

SEP = os.path.sep
INV_SEP = {"\\": '/', '/':'\\'}[os.path.sep]
NO_CONV = {"prompt", "negative_prompt", "url", "trace"}

def convert_path(p):
    return p.replace(INV_SEP, SEP)

def convert_all_paths(j):
    if type(j) == list:
        for i in range(len(j)):
            v = j[i]
            if type(v) == str and INV_SEP in v:
                j[i] = convert_path(v)
            if type(v) == list or type(v) == dict:
                convert_all_paths(j[i])
    elif type(j) == dict: 
        for k, v in j.items():
            if k in NO_CONV: continue
            if type(v) == str and INV_SEP in v:
                j[k] = convert_path(v)
            if type(v) == list or type(v) == dict:
                convert_all_paths(j[k])

def do_download(request, folder, id, callback):
    type = request["type"]
    url = request["url"]
    civitai_token = request.get("civitai_token", None)
    hf_token = request.get("hf_token", None)
    
    def started(callback, label, id):
        callback({"type":"download", "data":{"status": "started", "label": label}}, id)

    def success(callback, id, label=None):
        if label:
            callback({"type":"download", "data":{"status": "success", "label": label}}, id)
        else:
            callback({"type":"download", "data":{"status": "success"}}, id)
    
    def error(callback, err, id, trace=""):
        callback({"type":"download", "data":{"status": "error", "message": err, "trace": trace}}, id)

    def progress_callback(progress_data):
        """Handle progress updates from download manager"""
        try:
            status = progress_data.get('status', '')
            
            # Metadata updates
            if status == 'metadata':
                info = progress_data.get('info', {})
                callback({"type":"download", "data":{
                    "status": "metadata",
                    "base_model": info.get('base_model', ''),
                    "trained_words": info.get('trained_words', '')
                }}, id)
            
            # Progress updates
            elif 'progress' in progress_data or 'downloaded' in progress_data:
                progress = progress_data.get('progress', 0)
                downloaded = progress_data.get('downloaded', 0)
                total = progress_data.get('total', 0)
                
                # Convert to 0-1 range if needed
                if isinstance(progress, str):
                    try:
                        progress = float(progress.replace('%', '')) / 100
                    except:
                        progress = 0
                elif total > 0:
                    progress = min(1.0, downloaded / total)
                
                # Calculate speed (MB/s)
                rate_str = progress_data.get('speed', '0 KB/s')
                try:
                    if 'MB' in rate_str:
                        rate = float(rate_str.replace('MB/s', ''))
                    elif 'KB' in rate_str:
                        rate = float(rate_str.replace('KB/s', '')) / 1024
                    else:
                        rate = 0
                except:
                    rate = 0
                
                # Calculate ETA in seconds
                if downloaded > 0 and total > downloaded:
                    bytes_per_sec = max(rate * 1024 * 1024, 1)
                    eta = int((total - downloaded) / bytes_per_sec)
                else:
                    eta = 0
                
                callback({"type":"download", "data":{
                    "status": "progress",
                    "progress": min(1.0, progress),
                    "rate": rate,
                    "eta": eta,
                    "downloaded": downloaded,
                    "total": total
                }}, id)
            
            # Error updates
            elif status == 'error':
                error(callback, progress_data.get('error', 'Unknown error'), id)
            
            # Info messages
            elif status == 'info':
                message = progress_data.get('message', '')
                if message:
                    callback({"type":"download", "data":{
                        "status": "info",
                        "message": message
                    }}, id)
        
        except Exception as e:
            print(f"[Server] Progress callback error: {e}")
            error(callback, f"Progress tracking error: {e}", id)

    folder = os.path.join(folder, type)

    if not os.path.exists(folder):
        os.mkdir(folder)
    
    def execute_download():
        try:
            # Get the base models folder (parent of current type folder)
            # folder is like: /path/to/models/checkpoint
            # base_folder should be: /path/to/models
            base_folder = os.path.dirname(folder)
            
            print(f"[SERVER] Download started:")
            print(f"  URL: {url[:60]}...")
            print(f"  Type: {type}")
            print(f"  Folder: {folder}")
            print(f"  Base folder: {base_folder}")
            
            filename = download_manager.download_model(
                url=url,
                model_type=type,
                folder=base_folder,  # Pass parent folder, download_model will add type subfolder
                progress_callback=progress_callback,
                civitai_token=civitai_token,
                hf_token=hf_token
            )
            
            print(f"[SERVER] Download completed: {filename}")
            
            if filename:
                label = os.path.basename(filename)
                success(callback, id, label=label)
            else:
                error(callback, "Download failed", id)
        except Exception as e:
            trace = log_traceback("DOWNLOAD")
            print(f"[SERVER] Download error: {e}")
            error(callback, str(e), id, trace)

    thread = threading.Thread(target=execute_download)
    thread.start()

class Inference(threading.Thread):
    def __init__(self, wrapper, read_only, public, callback):
        super().__init__(daemon=True)
        
        self.wrapper = wrapper
        wrapper.callback = self.got_response

        self.callback = callback
        self.requests = queue.Queue()
        self.current = None

        self.read_only = read_only
        self.public = public
        self.owner = None

        self.stay_alive = True

    def got_response(self, response, id=None):
        if id == None:
            id = self.current
        return self.callback(id, response)

    def run(self):
        while self.stay_alive:
            try:
                client, self.current, request = self.requests.get(False)
                convert_all_paths(request)

                read_only = self.read_only and client != self.owner
                if read_only and request["type"] in {"convert", "manage", "download", "chunk"}:
                    raise Exception("Read-only")

                if request["type"] == "txt2img":
                    self.wrapper.reset()
                    self.wrapper.set(**request["data"])
                    self.wrapper.txt2img()
                elif request["type"] == "img2img":
                    self.wrapper.reset()
                    self.wrapper.set(**request["data"])
                    self.wrapper.img2img()
                elif request["type"] == "options":
                    self.wrapper.reset()
                    self.wrapper.options()
                elif request["type"] == "upscale":
                    self.wrapper.set(**request["data"])
                    self.wrapper.upscale()
                elif request["type"] == "convert":
                    self.wrapper.reset()
                    self.wrapper.set(**request["data"])
                    self.wrapper.convert()
                elif request["type"] == "manage":
                    self.wrapper.set(**request["data"])
                    self.wrapper.manage()
                elif request["type"] == "annotate":
                    self.wrapper.set(**request["data"])
                    self.wrapper.annotate()
                elif request["type"] == "segmentation":
                    self.wrapper.set(**request["data"])
                    self.wrapper.segmentation()
                elif request["type"] == "train_lora":
                    self.wrapper.set(**request["data"])
                    self.wrapper.train_lora()
                elif request["type"] == "train_upload":
                    self.wrapper.set(**request["data"])
                    self.wrapper.train_upload()
                elif request["type"] == "metadata":
                    self.wrapper.set(**request["data"])
                    self.wrapper.metadata()
                elif request["type"] == "download":
                    do_download(request["data"], self.wrapper.storage.path, self.current, self.got_response)
                elif request["type"] == "chunk":
                    self.upload(**request["data"])
                elif request["type"] == "ping":
                    self.got_response({"type":"pong"})
                self.requests.task_done()
            except queue.Empty:
                time.sleep(0.01)
            except Exception as e:
                self.requests.task_done()
                if str(e) == "Read-only":
                    self.got_response({"type":"error", "data":{"message": "Server is read-only"}})
                elif str(e) == "Aborted":
                    self.got_response({"type":"aborted", "data":{}})
                else:
                    additional = ""
                    trace = ""
                    try:
                        trace = log_traceback("SERVER")
                        s = traceback.extract_tb(e.__traceback__).format()
                        s = [e for e in s if not "venv" in e][-1]
                        s = s.split(", ")
                        file = s[0].split(os.path.sep)[-1][:-1]
                        line = s[1].split(" ")[1]
                        additional = f" ({file}:{line})"
                    except Exception as a:
                        trace = log_traceback("LOGGING")
                        additional = " THEN " + str(a)
                    self.got_response({"type":"error", "data":{"message":str(e) + additional, "trace": trace}})
            
            if self.public:
                self.wrapper.storage.clear_vram()
    
    def upload(self, type, name, chunk=None, index=-1, total=0):
        global UPLOAD_IDS
        rel_file = os.path.join(type, name)
        file = os.path.join(self.wrapper.storage.path, rel_file)
        os.makedirs(os.path.dirname(file), exist_ok=True)

        tmp = file + ".tmp"

        if index == 0:
            id = self.current
            UPLOAD_IDS[file] = id
            self.got_response({"type":"download", "data":{"status": "started", "label": rel_file.split(os.path.sep)[-1]}}, id)
            if os.path.exists(tmp):
                os.remove(tmp)

        id = UPLOAD_IDS[file]
        if chunk:
            with open(tmp, 'ab') as f:
                f.write(chunk)
            self.got_response({"type":"download", "data":{"status": "progress", "progress": index/total, "rate": 1, "eta": 0}}, id)
        else:
            if os.path.exists(tmp):
                os.rename(tmp, file)
            self.got_response({"type":"download", "data":{"status": "success"}}, id)

    def fetch(self, result_id, request_id, queue):
        def do_fetch():
            result = self.wrapper.fetch(result_id)
            if not result:
                return
            queue.put((request_id, result))

        thread = threading.Thread(target=do_fetch, args=([]), daemon=True)
        thread.start()

class Server():
    def __init__(self, wrapper, host, port, password=DEFAULT_PASSWORD, owner=False, read_only=False, monitor=False, public=False):
        self.stopping = False

        self.requests = {}
        self.clients = {}
        self.reconnected = {}

        self.scheme = None
        if password != None:
            self.scheme = get_scheme(password)

        self.monitor = monitor
        self.read_only = read_only
        self.owner = None if owner else "disabled"
        self.public = public

        self.inference = Inference(wrapper, read_only, public, callback=self.on_response)
        self.server = websockets.sync.server.serve(self.handle_connection, host=host, port=int(port), max_size=None)
        self.serve = threading.Thread(target=self.serve_forever, daemon=True)

    def start(self):
        print("SERVER: starting")
        self.inference.start()
        self.serve.start()

    def stop(self):
        print("SERVER: stopping")
        self.stopping = True
        self.inference.stay_alive = False
        print("SERVER: shutdown")
        self.server.shutdown()
        print("SERVER: join")
        self.join()
        print("SERVER: done")

    def join(self, timeout=None):
        self.serve.join(timeout)
        if self.serve.is_alive():
            return False # timeout
        self.inference.join()
        return True

    def serve_forever(self):
        self.server.serve_forever()

    def terminate_connection(self, connection):
        connection.protocol.send_frame = lambda x: None
        connection.socket.close()
        raise websockets.exceptions.ConnectionClosedError(None, None)

    def handle_connection(self, connection: websockets.sync.server.ServerConnection):
        new = True

        client_id = get_id()

        self.clients[client_id] = queue.Queue()
        self.clients[client_id].put((-1, {"type":"hello", "data":{"id":client_id}}))

        if self.owner == None:
            self.owner = client_id
            self.inference.owner = self.owner
            self.clients[client_id].put((-1, {"type":"owner"}))

        lost = False
        waiting = 0
        try:
            while not self.stopping:
                if not self.clients[client_id].empty():
                    id, response = self.clients[client_id].get()
                    response["id"] = id
                    data = encrypt(self.scheme, bson.dumps(response))
                    data = [data[i:min(i+FRAGMENT_SIZE,len(data))] for i in range(0, len(data), FRAGMENT_SIZE)]
                    connection.send(data)
                else:
                    data = None
                    try:
                        data = connection.recv(timeout=0)
                        waiting = 0
                    except TimeoutError:
                        pass
                    if not data:
                        time.sleep(0.01)
                        waiting += 10
                        if waiting >= 2000:
                            waiting = 0
                            pong = connection.ping()
                            #if not pong.wait(10):
                            #    self.terminate_connection(connection)

                        continue
                    error = None
                    request = None
                    if type(data) in {bytes, bytearray}:
                        try:
                            data = decrypt(self.scheme, bytes(data))
                            try:
                                request = bson.loads(data)
                            except:
                                error = "Malformed request"
                        except:
                            error = "Incorrect password"
                    else:
                        error = "Invalid request"
                    if request:
                        if request["type"] == "options" and new:
                            print(f"SERVER: client connected")
                            new = False
                        if request["type"] == "cancel":
                            id = request["data"]["id"]
                            if id in self.requests and self.requests[id] == client_id:
                                del self.requests[id]
                                self.send_response(client_id, id, {'type': 'aborted', 'data': {}})
                        if request["type"] == "reconnect":
                            old_client_id = request["data"]["id"]
                            if old_client_id in self.clients:
                                while not self.clients[old_client_id].empty():
                                    self.clients[client_id].put(self.clients[old_client_id].get())
                            self.reconnected[old_client_id] = client_id
                            for id in list(self.requests.keys()):
                                if self.requests[id] == old_client_id:
                                    self.requests[id] = client_id
                            
                        request_id = get_id()
                        if "id" in request:
                            request_id = request["id"]
                        self.requests[request_id] = client_id

                        if request["type"] == "fetch":
                            self.inference.fetch(request["data"]["id"], request_id, self.clients[client_id])
                            continue

                        remaining = self.inference.requests.unfinished_tasks
                        self.inference.requests.put((client_id, request_id, request))
                        self.clients[client_id].put((-1, {"type":"ack", "data":{"id": request_id, "queue": remaining}}))
                    else:
                        self.clients[client_id].put((-1, {"type":"error", "data":{"message": error}}))
        except websockets.exceptions.ConnectionClosedOK:
            pass
        except websockets.exceptions.ConnectionClosedError as e:
            if not e.rcvd and not e.sent:
                lost = True
        except Exception:
            log_traceback("CLIENT")

        if not new:
            if lost:
                print(f"SERVER: client lost, waiting...")
                for _ in range(60):
                    if client_id in self.reconnected:
                        print(f"SERVER: client found")
                        break
                    time.sleep(1)
            else:
                print(f"SERVER: client disconnected")

        if client_id in self.clients:
            del self.clients[client_id]

    def send_response(self, client, id, response):
        if client in self.clients:
            self.clients[client].put((id, response))
        if client != self.owner and self.monitor and self.owner in self.clients:
            response = response.copy()
            response["monitor"] = True
            self.clients[self.owner].put((id, response))

    def on_response(self, id, response):
        if self.stopping:
            return False
        if id in self.requests:
            client = self.requests[id]
            self.send_response(client, id, response)
            return client in self.clients
        else:
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='sd-inference-server')
    parser.add_argument('--bind', type=str, help='address (ip:port) to listen on', default="127.0.0.1:28888")
    parser.add_argument('--password', type=str, help='password to derive encryption key from', default=DEFAULT_PASSWORD)
    parser.add_argument('--models', type=str, help='models folder', default="../../models")
    parser.add_argument('--cache', type=int, help='number of models allowed to be cached in RAM', default=0)
    parser.add_argument('-r', '--read-only', help='disable filesystem changes', action='store_true')
    parser.add_argument('-o', '--owner', help='first client is the owner, bypassing read-only', action='store_true')
    parser.add_argument('-m', '--monitor', help='send all generations to the owner', action='store_true')
    parser.add_argument('-p', '--public', help='configure for multiple users (disables a few actions)', action='store_true')

    args = parser.parse_args()

    ip, port = args.bind.rsplit(":",1)

    model_storage = storage.ModelStorage(args.models, torch.float16, torch.float32, args.cache)
    params = wrapper.GenerationParameters(model_storage, torch.device("cuda"))

    if args.public:
        params.switch_public()

    server = Server(params, ip, port, args.password, args.owner, args.read_only, args.monitor, args.public)
    server.start()
    
    try:
        server.join()
    except KeyboardInterrupt:
        server.stop()
