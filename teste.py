import requests 

headers ={
    "Authorization":"Bearer yJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjIsImV4cCI6MTc4MDc3MzE4Mn0.bRkzg-TuyZ45IBj4ucwPuXWWPHbza6-Pr1ywKC4DqIo"
}

requisicao = requests.get("http://127.0.0.1:8000/login/refresh",headers=headers)
print(requisicao)
print(requisicao.json())