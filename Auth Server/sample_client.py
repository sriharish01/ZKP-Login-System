from __future__ import print_function
import logging

import grpc

import login_pb2
import login_pb2_grpc

import Crypto.Util.number
import random
import hashlib

def login():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = login_pb2_grpc.LoginStub(channel)
        stub = login_pb2_grpc.LoginStub(channel)
        password = "Hari2201"
        username = "sriharish"

        password_hash = hashlib.sha512(password.encode()).hexdigest()
        bits = 32
        x = sum(ord(c) << i*8 for i, c in enumerate(password_hash))
        p = Crypto.Util.number.getPrime(
            bits, randfunc=Crypto.Random.get_random_bytes)
        g = Crypto.Util.number.getPrime(
            bits, randfunc=Crypto.Random.get_random_bytes)
        while p == g:
            g = Crypto.Util.number.getPrime(
                bits, randfunc=Crypto.Random.get_random_bytes)

        print(x, p, g)
        r = random.getrandbits(bits) 
        c = pow(g, r, p)
        cipher = pow(g, ((x+r)%(p-1)), p)

        print(r, c, cipher)
        response = stub.Authenticate(login_pb2.LoginRequest(
            username=username, p=p, g=g, c=c, cipher=cipher))
    print("Login Result: " + str(response.response), response.id)


def register():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = login_pb2_grpc.LoginStub(channel)
        password = "Hari2201"
        username = "sriharish"
        email = "sriharish@email.com"
        
        response = stub.Register(login_pb2.RegisterRequest(
            username=username, password=hashlib.sha512(password.encode()).hexdigest(), email=email))
        
    print("Status " + str(response.status))


if __name__ == '__main__':
    logging.basicConfig()
    register()
    login()
