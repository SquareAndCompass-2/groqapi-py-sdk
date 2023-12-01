import os
import requests
import sys
import grpc
from datetime import datetime
from typing import Union
from typing import Literal
from typing import Any

sys.path.append(os.path.join(sys.path[0], "protogen"))
from public.llmcloud.requestmanager.v1 import (
    requestmanager_pb2,
    requestmanager_pb2_grpc,
)

from public.llmcloud.modelmanager.v1 import (
    modelmanager_pb2,
    modelmanager_pb2_grpc,
)

class GroqGrpcConnection:
    _grpc_channel = None
    _grpc_channel_async = None
    _auth_token = ""
    _auth_expiry_time = ""
    _API_URL = "api.groq.com:443"
    def _get_groq_key(self, renew=False):
        groq_access_key = os.environ.get("GROQ_SECRET_ACCESS_KEY")
        if self._auth_token != "" and renew is False:
            return self._auth_token

        if groq_access_key is None:
            print("Auth Token Error: Please set env variable GROQ_SECRET_ACCESS_KEY with the unique secret")
            sys.exit(1)

        Headers = {
            "Authorization": "Bearer " + groq_access_key,
        }
        AUTH_URL = "https://api.groq.com/v1/auth/get_token"
        auth_resp = requests.post(url=AUTH_URL, headers=Headers)
        self._auth_token = auth_resp.json()['access_token']
        self._auth_expiry_time = auth_resp.json()['expiry']

    def _is_past_expiry(self):
        return datetime.now() >= datetime.strptime(self._auth_expiry_time, '%Y-%m-%dT%H:%M:%SZ')

    def _get_grpc_credentials(self):
        if self._auth_token != "":
            if self._is_past_expiry():
                print("Renewing auth token")
                self._get_groq_key(renew=True)
            else:
                print("Reusing auth token")
        else:
            print("Getting auth token")
            self._get_groq_key(renew=True)

        credentials = grpc.ssl_channel_credentials()
        call_credentials = grpc.access_token_call_credentials(self._auth_token)
        credentials = grpc.composite_channel_credentials(credentials, call_credentials)
        return credentials

    def _open_grpc_channel(self) -> grpc.secure_channel:
        credentials = self._get_grpc_credentials()
        query_channel = grpc.secure_channel(self._API_URL, credentials)
        return query_channel

    def _open_grpc_channel_async(self) -> grpc.aio.secure_channel:
        credentials = self._get_grpc_credentials()
        query_channel = grpc.aio.secure_channel(self._API_URL, credentials)
        return query_channel

    def __init__(self):
        return

    def __del__(self):
        if self._grpc_channel is not None:
            self._grpc_channel.close()
            self._grpc_channel = None

    def get_grpc_channel(self):
        if self._grpc_channel is not None:
            if self._is_past_expiry():
                self._grpc_channel.close()
                self._auth_token = ""
                self._auth_expiry_time = ""
                self._grpc_channel = self._open_grpc_channel()
        else:
            self._grpc_channel = self._open_grpc_channel()

        return self._grpc_channel

    async def __aexit__(self):
        if self._grpc_channel_async is not None:
            self._grpc_channel_async.aio.close()
            self._grpc_channel_async = None

    def get_grpc_channel_async(self):
        if self._grpc_channel_async is not None:
            if self._is_past_expiry():
                self._grpc_channel_async.aio.close()
                self._auth_token = ""
                self._auth_expiry_time = ""
                self._grpc_channel_async = self._open_grpc_channel_async()
        else:
            self._grpc_channel_async = self._open_grpc_channel_async()

        return self._grpc_channel_async

grpc_connection = GroqGrpcConnection()

class Models:
    def __init__(self):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel()
        self._stub = modelmanager_pb2_grpc.ModelManagerServiceStub(self._query_channel)

    def list_models(self):
        request = modelmanager_pb2.ListModelsRequest()
        resp = self._stub.ListModels(request)
        return resp

class ChatCompletion:
    def __init__(self, model):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel()
        self._stub = requestmanager_pb2_grpc.RequestManagerServiceStub(self._query_channel)
        self._model = model
        self._system_prompt = "Give useful and accurate answers."
        self._lastmessages = []
        self._history_index = 0

    def __del__(self):
        self._lastmessages = []

    def __enter__(self):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel()
        return self

    def __exit__(self, *args: object) -> None:
        self._lastmessages = []
        return None

    def _update_history(self, user_prompt, response):
        self._lastmessages.append({"user_prompt" : user_prompt, "last_resp" : response})

    def _resp_generator(self, resp_stream):
        for response in resp_stream:
            if self._history_index > -1:
                self._lastmessages[self._history_index]["last_resp"] += response.content
            yield response

    def send_chat(
        self,
        user_prompt = "Write multiple paragraphs",
        streaming=False,
        seed=1234,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
    ) -> Union[tuple[Literal[''], Literal[''], dict] , Any]:
        # Generate request
        request = requestmanager_pb2.GetTextCompletionRequest()
        request.user_prompt = user_prompt

        history_messages = -1
        for msg in self._lastmessages:
            history_messages += 1
            req = request.history.add()
            req.user_prompt = msg["user_prompt"]
            req.assistant_response = msg["last_resp"]

        self._history_index = history_messages

        request.model_id = self._model
        request.system_prompt = self._system_prompt
        request.seed = seed
        request.max_tokens = max_tokens
        request.temperature = temperature
        request.top_p = top_p
        request.top_k = top_k

        try:
            if streaming == True:
                resp_stream = self._stub.GetTextCompletionStream(request)
            else:
                resp = self._stub.GetTextCompletion(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                print('Invalid Args. Please check model name and other params')
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                print(f"grpc error: {e.details()}. Requested model maybe currently offline.")
            else:
                raise e
            return "", "", {}

        if streaming == True:
            self._update_history(user_prompt, "")
            return self._resp_generator(resp_stream=resp_stream)
        else:
            self._update_history(user_prompt, resp.content)
            return resp.content, resp.request_id, resp.stats

class Completion:
    def __init__(self):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel()
        self._stub = requestmanager_pb2_grpc.RequestManagerServiceStub(self._query_channel)

    def __del__(self):
        return

    def __enter__(self):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel()
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def _resp_generator(self, resp_stream):
        for response in resp_stream:
            yield response

    def send_prompt(
        self,
        model,
        user_prompt = "Write multiple paragraphs",
        system_prompt="Give useful and accurate answers.",
        streaming=False,
        seed=1234,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
    ) -> Union[tuple[Literal[''], Literal[''], dict] , Any]:
        # Generate request
        request = requestmanager_pb2.GetTextCompletionRequest()
        request.user_prompt = user_prompt
        request.model_id = model
        request.system_prompt = system_prompt
        request.seed = seed
        request.max_tokens = max_tokens
        request.temperature = temperature
        request.top_p = top_p
        request.top_k = top_k

        try:
            if streaming == True:
                resp_stream = self._stub.GetTextCompletionStream(request)
            else:
                resp = self._stub.GetTextCompletion(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                print('Invalid Args. Please check model name and other params')
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                print(f"grpc error: {e.details()}. Requested model maybe currently offline.")
            else:
                raise e
            return "", "", {}
        
        if streaming == True:
            return self._resp_generator(resp_stream=resp_stream)
        else:
            return resp.content, resp.request_id, resp.stats


class AsyncCompletion:
    def __init__(
        self,
        model,
        user_prompt = "Write multiple paragraphs",
        system_prompt="Give useful and accurate answers.",
        streaming=False,
        seed=1234,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
    ):
        global grpc_connection
        self._query_channel_async = grpc_connection.get_grpc_channel_async()
        self._stub = requestmanager_pb2_grpc.RequestManagerServiceStub(self._query_channel_async)

    async def __aenter__(self):
        global grpc_connection
        self._query_channel_async = grpc_connection.get_grpc_channel_async()
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def _resp_generator(self, resp_stream):
        async for response in resp_stream:
            yield response

    async def send_prompt(
        self,
        model,
        user_prompt = "Write multiple paragraphs",
        system_prompt="Give useful and accurate answers.",
        streaming=False,
        seed=1234,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
    ) -> Union[tuple[Literal[''], Literal[''], dict] , Any]:
        # Generate request
        request = requestmanager_pb2.GetTextCompletionRequest()
        request.user_prompt = user_prompt
        request.model_id = model
        request.system_prompt = system_prompt
        request.seed = seed
        request.max_tokens = max_tokens
        request.temperature = temperature
        request.top_p = top_p
        request.top_k = top_k

        try:
            if streaming == True:
                resp_stream = self._stub.GetTextCompletionStream(request)
            else:
                resp = await self._stub.GetTextCompletion(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                print('Invalid Args. Please check model name and other params')
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                print(f"grpc error: {e.details()}. Requested model maybe currently offline.")
            else:
                raise e
            return "", "", {}

        if streaming == True:
            return self._resp_generator(resp_stream=resp_stream)
        else:
            return resp.content, resp.request_id, resp.stats

class AsyncChatCompletion:
    def __init__(self, model):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel_async()
        self._stub = requestmanager_pb2_grpc.RequestManagerServiceStub(self._query_channel)
        self._model = model
        self._system_prompt = "Give useful and accurate answers."
        self._lastmessages = []
        self._history_index = 0

    def __del__(self):
        self._lastmessages = []

    async def __aenter__(self):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel_async()
        return self

    async def __aexit__(self, *args: object) -> None:
        self._lastmessages = []
        return None

    def _update_history(self, user_prompt, response):
        self._lastmessages.append({"user_prompt" : user_prompt, "last_resp" : response})

    async def _resp_generator(self, resp_stream):
        async for response in resp_stream:
            if self._history_index > -1:
                self._lastmessages[self._history_index]["last_resp"] += response.content
            yield response

    async def send_chat(
        self,
        user_prompt = "Write multiple paragraphs",
        streaming=False,
        seed=1234,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
    ) -> Union[tuple[Literal[''], Literal[''], dict] , Any]:
        # Generate request
        request = requestmanager_pb2.GetTextCompletionRequest()
        request.user_prompt = user_prompt

        history_messages = -1
        for msg in self._lastmessages:
            history_messages += 1
            req = request.history.add()
            req.user_prompt = msg["user_prompt"]
            req.assistant_response = msg["last_resp"]

        self._history_index = history_messages

        request.model_id = self._model
        request.system_prompt = self._system_prompt
        request.seed = seed
        request.max_tokens = max_tokens
        request.temperature = temperature
        request.top_p = top_p
        request.top_k = top_k

        try:
            if streaming == True:
                resp_stream = self._stub.GetTextCompletionStream(request)
            else:
                resp = await self._stub.GetTextCompletion(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                print('Invalid Args. Please check model name and other params')
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                print(f"grpc error: {e.details()}. Requested model maybe currently offline.")
            else:
                raise e
            return "", "", {}

        if streaming == True:
            self._update_history(user_prompt, "")
            return self._resp_generator(resp_stream=resp_stream)
        else:
            self._update_history(user_prompt, resp.content)
            return resp.content, resp.request_id, resp.stats
