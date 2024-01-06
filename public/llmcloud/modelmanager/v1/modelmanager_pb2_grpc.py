# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from public.llmcloud.modelmanager.v1 import (
    modelmanager_pb2 as public_dot_llmcloud_dot_modelmanager_dot_v1_dot_modelmanager__pb2,
)


class ModelManagerServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ListModels = channel.unary_unary(
            "/public.llmcloud.modelmanager.v1.ModelManagerService/ListModels",
            request_serializer=public_dot_llmcloud_dot_modelmanager_dot_v1_dot_modelmanager__pb2.ListModelsRequest.SerializeToString,
            response_deserializer=public_dot_llmcloud_dot_modelmanager_dot_v1_dot_modelmanager__pb2.ListModelsResponse.FromString,
        )


class ModelManagerServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ListModels(self, request, context):
        """lists all available models a client can select"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_ModelManagerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "ListModels": grpc.unary_unary_rpc_method_handler(
            servicer.ListModels,
            request_deserializer=public_dot_llmcloud_dot_modelmanager_dot_v1_dot_modelmanager__pb2.ListModelsRequest.FromString,
            response_serializer=public_dot_llmcloud_dot_modelmanager_dot_v1_dot_modelmanager__pb2.ListModelsResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "public.llmcloud.modelmanager.v1.ModelManagerService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class ModelManagerService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ListModels(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/public.llmcloud.modelmanager.v1.ModelManagerService/ListModels",
            public_dot_llmcloud_dot_modelmanager_dot_v1_dot_modelmanager__pb2.ListModelsRequest.SerializeToString,
            public_dot_llmcloud_dot_modelmanager_dot_v1_dot_modelmanager__pb2.ListModelsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
