from flask import Flask, request, render_template, redirect

from bson.json_util import dumps
import pymongo
import dns

from pymongo import MongoClient

from flask_socketio import SocketIO, emit
import logging

app = Flask('app')
app.debug = False

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

socketio = SocketIO(
    app, async_mode='threading', cors_allowed_origins="*", logger=False, engineio_logger=False)

client = MongoClient(
    "mongodb+srv://root:root@cluster0-0rj95.mongodb.net/test?retryWrites=true")
db = client.registros

#db.registros.delete_many({'titulo' : "NOS4A2"})

@app.route('/')
def hello_world():   
    return render_template('busca.html')

@socketio.on('preferido')
def preferido(im, nome):
    print("Preferido:" + im)
    print(db.preferidos.find({'imdb':im}).count())
    if db.preferidos.find({'imdb':im}).count() == 0:
        db.preferidos.insert_one({
        	'imdb': im,
			'nome': nome
    	})

@socketio.on('remove_preferido')
def remove_preferido(im):
    print("Não Preferido:" + im)
    db.preferidos.delete_many({
        'imdb':im
    })

@socketio.on('apagar')
def apagar(im):
    print("Apagado: " + im)
    db.registros.delete_many({'imdb': {'$regex': '.*'+im}})
    
@socketio.on('carregar_preferidos')
def sock_navegar():		
	socketio.emit('resposta_preferidos', dumps(db.preferidos.find()))

@socketio.on('buscar_im')
def buscar_im(nome):
    print("Buscando IMDB: " + nome)    
    socketio.emit('carregado_im', dumps(db.registros.find(
		{"$or":[{
            'nome': {
                '$regex': '.*'+nome+'.*'
            }
			},
            {'titulo': {
                '$regex': '.*'+nome+'.*'
            }
			}]}
			)))

@socketio.on('inicio')
def sock_iniciado():
    print('inicio')
    #socketio.start_background_task(thread_lista, 'https://hidratorrent.com/lancamentos-', 3)

@socketio.on('connect')
def test_connect():
    print('conectado')

@socketio.on('tabela')
def sock_tabela():
    socketio.emit('carregar_tabela', dumps(db.registros.find({})))

if __name__ == "__main__":
	socketio.run(app,  debug=False,  host='0.0.0.0', port=3000)



