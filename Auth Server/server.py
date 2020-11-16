from concurrent import futures
import logging

import grpc

import login_pb2
import login_pb2_grpc
import pymysql

class Login(login_pb2_grpc.LoginServicer):

    def Register(self, request, context):
        db = pymysql.connect(host='localhost',user='root',password='Hari2201',db='ZKP',port=3306, cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()

        username = request.username
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username))
            account = cursor.fetchone()
            if account:
                return login_pb2.RegisterResponse(status = login_pb2.RegisterResponse.Status.ALREADY_EXISTS)
            else:
                password = request.password
                email = request.email
                cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s)', (username, password, email))
                db.commit()
                return login_pb2.RegisterResponse(status = login_pb2.RegisterResponse.Status.SUCCESS)
        except Exception as e:
            print(e.args)
            return login_pb2.RegisterResponse(status = login_pb2.RegisterResponse.Status.ERROR)

    def Authenticate(self, request, context):
        username = request.username
        p = request.p
        g = request.g
        c = request.c
        cipher = request.cipher

        db = pymysql.connect(host='localhost',user='root',password='Hari2201',db='ZKP',port=3306, cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        query = "SELECT id, username,password FROM users WHERE username = \"" + username + "\""
        try:
            rows_count = cursor.execute(query)
            result = cursor.fetchone()
            if rows_count == 0:
                return login_pb2.LoginReply(response=False)
            else:
                # print (result)
                password = result["password"]
                x = sum(ord(c) << i*8 for i, c in enumerate(password))
                # print (x)
                y = pow(g, x, p)
                my_cipher =  (c*y)%p
                if my_cipher == cipher:
                    return login_pb2.LoginReply(response=True , id = result["id"])
                else:
                    return login_pb2.LoginReply(response=False)
        except:
                print("Unexpected Auth Error")
                return login_pb2.LoginReply(response=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    login_pb2_grpc.add_LoginServicer_to_server(Login(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()