# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from public.llmcloud.queuestatemanager.v1 import (
    queuestatemanager_pb2 as public_dot_llmcloud_dot_queuestatemanager_dot_v1_dot_queuestatemanager__pb2,
)


class QueueStateManagerServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetRequestState = channel.unary_unary(
            "/public.llmcloud.queuestatemanager.v1.QueueStateManagerService/GetRequestState",
            request_serializer=public_dot_llmcloud_dot_queuestatemanager_dot_v1_dot_queuestatemanager__pb2.GetRequestStateRequest.SerializeToString,
            response_deserializer=public_dot_llmcloud_dot_queuestatemanager_dot_v1_dot_queuestatemanager__pb2.GetRequestStateResponse.FromString,
        )


class QueueStateManagerServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetRequestState(self, request, context):
        """Returns the request's place in the queue"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_QueueStateManagerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetRequestState": grpc.unary_unary_rpc_method_handler(
            servicer.GetRequestState,
            request_deserializer=public_dot_llmcloud_dot_queuestatemanager_dot_v1_dot_queuestatemanager__pb2.GetRequestStateRequest.FromString,
            response_serializer=public_dot_llmcloud_dot_queuestatemanager_dot_v1_dot_queuestatemanager__pb2.GetRequestStateResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "public.llmcloud.queuestatemanager.v1.QueueStateManagerService",
        rpc_method_handlers,
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class QueueStateManagerService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetRequestState(
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
            "/public.llmcloud.queuestatemanager.v1.QueueStateManagerService/GetRequestState",
            public_dot_llmcloud_dot_queuestatemanager_dot_v1_dot_queuestatemanager__pb2.GetRequestStateRequest.SerializeToString,
            public_dot_llmcloud_dot_queuestatemanager_dot_v1_dot_queuestatemanager__pb2.GetRequestStateResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
