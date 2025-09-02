from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from os import getenv

MONGO_URI = getenv("MONGO_URI", "mongodb://mongodb:27017/")
client = MongoClient(MONGO_URI)
db = client["lanchonete"]

app = FastAPI()

#modelos
class Cliente(BaseModel):
    nome: str
    email: str  
    cidade: str

class Produto(BaseModel):
    nome: str
    categoria: str
    preco: float

class Pedido(BaseModel):
    cliente_id: str
    produtos_id: List[str]
    data: datetime = Field(default_factory=datetime.utcnow)



#endpoint clientes
@app.post("/clientes")
def criar_cliente(cliente: Cliente):
    result = db.clientes.insert_one(cliente.dict())
    return {"id": str(result.inserted_id)}

@app.get("/clientes")
def listar_clientes():
    return list(db.clientes.find({}, {"_id": 0}))

#endpoint produto
@app.post("/produtos")
def criar_produto(produto: Produto):
    result = db.produtos.insert_one(produto.dict())
    return {"id": str(result.inserted_id)}

@app.get("/produtos")
def listar_produtos():
    produtos = list(db.produtos.find({}))
    for i in produtos:
        i["_id"] = str(i["_id"])
    return produtos

#endpoint pedidos
@app.post("/pedidos")
def criar_pedido(pedido: Pedido):
    result = db.pedidos.insert_one(pedido.dict())
    return {"id": str(result.inserted_id)}

@app.get("/pedidos")
def listar_pedidos():
    pedidos = list(db.pedidos.find({}))
    for p in pedidos:
        p["_id"] = str(p["_id"])
    return pedidos

#cadastro
@app.on_event("cadastro")
def cadastro():
    if db.clientes.count_documents({}) == 0:
        db.clientes.insert_many([
            {"nome": "Felipe França", "email": "felipe@gmail.com", "cidade": "São Paulo"},
            {"nome": "Bruno Maurus", "email": "bruno@gmail.com", "cidade": "Salvador"},
            {"nome": "Arthur Callegari", "email": "Arthur@email.com", "cidade": "Osasco"}
        ])

    if db.produtos.count_documents({}) == 0:
        db.produtos.insert_many([
            {"nome": "pão de batata", "categoria": "salgados", "preco": 6.00},
            {"nome": "coxinha", "categoria": "salgados", "preco": 5.50},
            {"nome": "café", "categoria": "bebidas", "preco": 3.00}
        ])

    if db.pedidos.count_documents({}) == 0:
        db.pedidos.insert_many([
            {"cliente_id": "1", "produtos_id": ["1", "2"], "data": datetime.utcnow()},
            {"cliente_id": "2", "produtos_id": ["3"], "data": datetime.utcnow()},
            {"cliente_id": "3", "produtos_id": ["1", "3"], "data": datetime.utcnow()}
        ])

#endpoints de consulta
#pedidos de um cliente específico
@app.get("/pedidos/cliente/{cliente_id}") #http://localhost:8000/pedidos/cliente/1
def pedidos_cliente(cliente_id: str):
    pedidos = list(db.pedidos.find({"cliente_id": cliente_id}))
    if not pedidos:
        return {"mensagem": "Nenhum pedido encontrado para este cliente."}

    for p in pedidos:
        p["_id"] = str(p["_id"])
        p["data"] = p["data"].strftime("%d/%m/%Y %H:%M:%S")
    return pedidos

#produtos de uma determinada categoria
@app.get("/produtos/categoria/{categoria}") #http://localhost:8000/produtos/categoria/salgados
def produtos_categoria(categoria: str):
    produtos = list(db.produtos.find({"categoria": categoria}))
    if not produtos:
        return {"mensagem""nenhum produto encontrado nesta categoria."}
    
    for i in produtos:
        i["_id"] = str(i["_id"])
    return produtos

#cidades dos clientes
@app.get("/clientes/cidade") #http://localhost:8000/clientes/cidade
def clientes_nome_cidade():
    clientes = list(db.clientes.find({}, {"_id": 0, "nome": 1, "cidade": 1}))
    return clientes

#pedidos ordenados
@app.get("/pedidos/ordenados") #http://localhost:8000/pedidos/ordenados
def pedidos_ordenados():
    pedidos = list(db.pedidos.find().sort("data", -1))
    for p in pedidos:
        p["_id"] = str(p["_id"])
        p["data"] = p["data"].strftime("%d/%m/%Y %H:%M:%S")
    return pedidos