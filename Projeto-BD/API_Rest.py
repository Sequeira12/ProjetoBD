##
# ==============================================
# ============== Bases de Dados ================
# ============== LEI  2021/2022 ================
# ==============================================
# === Department of Informatics Engineering ====
# =========== University of Coimbra ============
# ==============================================
# ==============================================
# ==============================================
# ==============================================
# = Bruno Eduardo Machado Sequeira (2020235721)=
# =     uc2020235721@student.uc.pt             =
# = Ricardo Rafael Ferreira Guegan (2020211358)=
# =     uc2020211358@student.uc.pt             =
# ==============================================
# ==============================================


import sys
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from datetime import datetime
from functools import wraps
import time
app =   Flask(__name__)
import psycopg2
api = Api(app)
import logging
import jwt
StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

def connect_db():
    connection = psycopg2.connect(user = sys.argv[1],
        password = sys.argv[2],
        host = str(sys.argv[3]),
        port = sys.argv[4],
        database = sys.argv[5]

    )

    return connection







def connect_db2():
    connection = psycopg2.connect(user = "brunosequeira",
        password = "",
        host = "127.0.0.1",
        port = "5432",
        database = "TesteFinal"

    )

    return connection


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            id_user = -1
            return f(id_user, *args, **kwargs)

        try:
            data = jwt.decode(token, "Tykki", algorithms=["HS256"])
            id_user = data['id_user']
            tempo = data['data']
            if(time.time() - 1800 > tempo):
                return {'status': StatusCodes['internal_error'], 'errors': 'Token expirado'}

        except:
            return {'status': StatusCodes['internal_error'], 'errors': 'Utilizador não existe/Password Incorreta'}

        return f(id_user, *args, **kwargs)

    return decorated


class Login(Resource):
    def get(self, nome, password):
        conn = connect_db()
        cur = conn.cursor()
        try:

            passEncode = jwt.encode({'password': password}, "Tykki", algorithm='HS256')
            print(passEncode)
            cur.execute('SELECT id_user FROM utilizador WHERE username= %s and password = %s', (nome, passEncode))
            row = cur.fetchall()
            linha = row[0]
            id_user = linha[0]

            token_user = jwt.encode({'id_user': id_user,'data':time.time()}, "Tykki", algorithm='HS256')
            return jsonify({'token': token_user})
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'GET /login - error: {error}')
            response = {'status': StatusCodes['internal_error'], 'errors': 'Utilizador não existe'}

        finally:
            if conn is not None:
                conn.close()
        return response


api.add_resource(Login, "/login/<string:nome>/<string:password>")



#######################################       ADD UTILIZADORES                        ################################################
@app.route('/user/',methods=['POST'])
@token_required
def add_utilizadores(id_user):

    logger.info('POST /vendedor')
    payload = request.get_json()
    conn = connect_db()
    cur = conn.cursor()

    if(id_user != -1):
        type = 0
        cur.execute('select * from admin where user_id_user=%s',str(id_user))
        if (cur.rowcount == 0):
            conn.close()
            return jsonify("Administrador não existente!")
    else:
        type = 1
    try:
        pass_Encript = jwt.encode({'password': payload["password"]}, "Tykki", algorithm='HS256')      #        jwt.encode({'password': payload["password"]}, "Tykki", algorithm='HS256')
        cur.execute('INSERT INTO utilizador (username, password, email) VALUES ( %s,   %s,   %s)',(payload["username"],pass_Encript,payload["email"]))

        cur.execute('select id_user from utilizador where username = %s and password= %s and email = %s',(payload["username"],
                    pass_Encript,payload["email"]))
        row = cur.fetchall()
        print(row)
        id = row[0]
        if(type == 1):
            statement = 'INSERT INTO comprador(name_comp,nif_comp,morada,n_cartao,user_id_user) values(%s,%s,%s,%s,%s)'
            values = (payload["name_comp"], payload["nif"], payload["morada"], payload["n_cartao"], id)
            cur.execute(statement, values)
            cur.execute("commit")
        else:
            if(payload["type"] == "vendedor"):
                values = (payload["name_vend"], payload["nif"], payload["morada_envio"], True, id)
                statement = 'INSERT INTO vendedor(name_vend,nif,morada_envio,Aprovacao,user_id_user) values(%s,%s,%s,%s,%s)'
                cur.execute(statement, values)

            if(payload["type"] == "administrador"):
                values = (payload["name"], payload["anodeservico"], payload["salario"],id)
                statement = 'INSERT INTO admin(name,anodeservico,salario,user_id_user) values(%s,%s,%s,%s)'
                cur.execute(statement,values)
        cur.execute("commit")
        response = {'status': StatusCodes['success'], 'results': f'Inserted Utilizador {payload["username"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user/ - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)

########################################################################################################################
################################################### - get produtos _- ##################################################
######################################################## FEITO #########################################################
########################################################################################################################
@app.route('/produtos/',methods=['GET'])
def get_produtos():
    logger.info('GET /produtos/')

    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM produto where versao=true')
        rows = cur.fetchall()

        logger.debug('GET /produto - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'id': row[0],'nome': row[1], 'preco': row[2],'marca': row[3], 'peso': row[4],'stock': row[5], 'codigobarras': row[6]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /produtos/ - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)

########################################################################################################################
###############################     UPDATE PRODUTOS      ###############################################################
####################################### FEITO ##########################################################################
########################################################################################################################
@app.route("/produto/update/<id>", methods=['PUT'])
@token_required
def update_Produtos(id_user,id):
    logger.info('POST /produtos/update/<id>')
    payload = request.get_json()
    conn = connect_db()
    cur = conn.cursor()

    logger.debug(f'ID: {id}')

    if (id_user != -1):
        a = "select * from vendedor where user_id_user=" + str(id_user)
        cur.execute(a)
        if (cur.rowcount == 0):
            return jsonify("Vendedor não existente!")
    else:
        return jsonify("Token inesxistente")

    cur.execute(
        "SELECT * from produto where id_produto = %s and vendedor_user_id_user=%s",(id,id_user))

    if (cur.rowcount == 0):
        conn.close()
        return jsonify("Não possui esse Produto!")

    try:
        cur.execute(
            "SELECT codigobarras from produto where id_produto = %s and vendedor_user_id_user=%s", (id, id_user))
        row = cur.fetchall()
        codigo = row[0]

        cur.execute("SELECT * from TV where produto_codigobarras=%s",(codigo))

        if(cur.rowcount==0):
            cur.execute("SELECT * from smartphone where produto_codigobarras=%s",(codigo))
            if(cur.rowcount == 0):
                cur.execute("SELECT * from computador where produto_codigobarras=%s",(codigo))
                if(cur.rowcount != 0):
                    type = "computador"
            else:
                type = "smartphone"
        else:
            type = "TV"
        if(payload["type"] != type):
            return jsonify("Type é diferente!")

        cur.execute('UPDATE produto SET versao=false where id_produto=%s',id)


        cur.execute('select max(codigobarras) from produto',id)
        row = cur.fetchall()

        newCode = '0000000'+str(int(row[0][0])+1)

        cur.execute('insert into produto(id_produto,nome,preco,marca,peso,stock,codigobarras,Versao,vendedor_user_id_user) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (id, payload["nome"], payload["preco"], payload["marca"], payload["peso"], payload["stock"],
             newCode, True, id_user))
        if payload["type"] == "TV":

            cur.execute('insert into tv (definicao,smartv,dimensao_,produto_codigobarras)values(%s,%s,%s,%s)',
                    (payload["definicao"], payload["smartv"], payload["dimensao_"], newCode))
        if payload["type"] == "smartphone":
            cur.execute(
                'insert into smartphone(memoria,resolucao_camara,bateria,processador,ecra,produto_codigobarras)values(%s,%s,%s,%s)',
                (payload["memoria"], payload["resolucao_camara"], payload["bateria"], payload["processador"],
                 payload["ecra"], newCode))

        if payload["type"] == "computador":
            cur.execute(
                'insert into computadr(ram,processador,bateria,ecra,produto_codigobarras)values(%s,%s,%s,%s)',
                (payload["ram"], payload["processador"], payload["bateria"], payload["ecra"], newCode))


        cur.execute("commit")

        response = {'status': StatusCodes['success'], 'results': f'Update produto {payload["nome"]}'}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /produto/update/<id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)

########################################################################################################################
########################################       ADD-PRODUTOS      #######################################################
################################################ FEITO #################################################################
########################################################################################################################


@app.route('/produtos/',methods=['POST'])
@token_required
def add_produtos(id_user):
    logger.info('POST /produtos')
    print(id_user)

    payload = request.get_json()
    conn = connect_db()
    cur = conn.cursor()
    if(id_user != -1):
        a = "select * from vendedor where user_id_user=" +str(id_user) # melhorar isto

        cur.execute(a)
        if (cur.rowcount == 0):
            return jsonify("Vendedor não existente!")
    else:
        return jsonify("Token inesxistente")

    try:
        cur.execute('select max(id_produto) from produto')
        rows = cur.fetchall()
        idp = rows[0][0]
        if(idp == None):
            idp = 0
        else:
            idp+=1
        codigo = '0000000' + str(int(idp)+1)

        cur.execute(
            'insert into produto(id_produto,nome,preco,marca,peso,stock,codigobarras,Versao,vendedor_user_id_user) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (idp, payload["nome"], payload["preco"], payload["marca"], payload["peso"], payload["stock"], codigo, True,
             id_user))
        if payload["type"] == "TV":
              cur.execute('insert into tv(definicao,smartv,dimensao_,produto_codigobarras)values(%s,%s,%s,%s)',(payload["definicao"],payload["smartv"],payload["dimensao_"],codigo))
        if payload["type"] == "smartphone":
            cur.execute('insert into smartphone(memoria,resolucao_camara,bateria,processador,ecra,produto_codigobarras)values(%s,%s,%s,%s,%s,%s)',
                        (payload["memoria"], payload["resolucao"], payload["bateria"],True,payload["ecra"],codigo))

        if payload["type"] == "computador":
           cur.execute('insert into computador(ram,processador,bateria,ecra,produto_codigobarras)values(%s,%s,%s,%s,%s)', (payload["ram"], payload["processador"], payload["bateria"], payload["ecra"], codigo))

        cur.execute("commit")

        response = {'status': StatusCodes['success'], 'results': f'Inserted Produto {payload["nome"]}'}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /produtos - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)


########################################################################################################################
###################################     INFO UTILIZADORES   ############################################################
############################################# FEITO ####################################################################
@app.route('/utilizador/', methods=['GET'])
@token_required
def get_utilizadores(id_user):
    logger.info('GET /utilizador')

    conn = connect_db()
    cur = conn.cursor()
    if (id_user != -1):

        cur.execute('select * from admin where user_id_user=%s',(id_user,))
        if (cur.rowcount == 0):
            response = {'status': StatusCodes['internal_error'], 'errors': 'Não tem permissão'}
            return jsonify(response)
    else:
        response = {'status': StatusCodes['internal_error'], 'errors': 'Token inexistente'}
        return jsonify(response)

    try:
        cur.execute('SELECT * FROM utilizador')
        rows = cur.fetchall()

        logger.debug('GET /departments - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'id_user': row[0],'username': row[1], 'password': row[2], 'email': row[3]}
            Results.append(content)

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /utilizador - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)

########################################################################################################################
######################################       REALIZAR COMPRA       #####################################################
##############################################NAO TA FEITO  ############################################################

@app.route('/order/', methods=['POST'])
@token_required
def Realiza_Compra(id_user):

    logger.info('POST /vendedor')
    payload = request.get_json()
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('select * from comprador where user_id_user=%s',(id_user,))
    if(id_user != -1):
        if(cur.rowcount == 0):
            response = {'status': StatusCodes['success'], 'results': 'Não é comprador'}
            return jsonify(response)
    else:
        response = {'status': StatusCodes['success'], 'results': 'Token inexistente'}
        return jsonify(response)
    try:
        cur.execute('select max(n_compra) from encomenda')
        row = cur.fetchall()



        if(row[0][0] == None):
            nCompra = 1
        else:
            nCompra = row[0][0] + 1
        ncompra = str(nCompra)
        id = str(id_user)


        valor = (ncompra,str(datetime.utcnow()),'0', id)


        cur.execute("insert into encomenda(n_compra,dataCompra,preco_total,comprador_user_id_user) values(%s,'%s',%s,%s)"%valor)

        precoTotal = 0

        lista = payload["cart"]

        for i in range(len(lista)):

            idProduto = lista[i][0]
            quantidade = lista[i][1]
            cur.execute('select codigobarras,preco from produto where id_produto=%s and versao=true'%(str(idProduto),))
            if(cur.rowcount == 0):
                conn.rollback()
            table = cur.fetchall()
            codigo = table[0][0]
            preco = table[0][1]

            values = (str(quantidade),codigo,str(nCompra))
            precoTotal += int(preco) * int(quantidade)

            cur.callproc('compra',[quantidade,codigo,nCompra])

            cur.execute('insert into par_prod_quant(quantidade, produto_codigobarras,encomenda_n_compra)values(%s,%s,%s)',values)


        values = (precoTotal, nCompra)
        cur.execute('UPDATE encomenda SET preco_total=%s where n_compra=%s',values)

        cur.execute('commit')
        response = {'status': StatusCodes['success'], 'results': f'Inserted Encomenda'}


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /order - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)

########################################################################################################################
######################                  RATING DE UM PRODUTO  ##########################################################
############################################# FEITO #############################################################
########################################################################################################################
@app.route('/rating/<id>', methods=['POST'])
@token_required
def Rating(id_user,id):

    logger.info('POST /vendedor')
    payload = request.get_json()
    conn = connect_db()
    cur = conn.cursor()


    cur.execute('select codigobarras from produto where id_produto=%s',str(id))
    if(id_user != -1):

        if(cur.rowcount == 0):
            response = {'status': StatusCodes['internal_error'], 'errors': 'Não Existe esse Produto!'}
            return jsonify(response)
    else:
        response = {'status': StatusCodes['success'], 'results': 'Token inexistente'}
        return jsonify(response)
    row = cur.fetchall()
    CodigoProduto = row[0][0]

    cur.execute('select * from rating_comprador where rating_produto_codigobarras=%s and comprador_user_id_user=%s',(CodigoProduto,id_user,))
    if(cur.rowcount > 0):
        response = {'status': StatusCodes['internal_error'], 'errors': 'Já deu rating a este produto!'}
        return jsonify(response)
    
    cur.execute('select count(*) from encomenda join par_prod_quant on encomenda.n_compra = par_prod_quant.encomenda_n_compra where encomenda.comprador_user_id_user = %s and par_prod_quant.produto_codigobarras = %s',(id_user,CodigoProduto))
    row = cur.fetchall()

    if(row[0][0]== 0):
        response = {'status': StatusCodes['internal_error'], 'errors': 'Não Comprou esse produto'}
        return jsonify(response)
    if(payload["rating"] < 0 or payload["rating"] > 5):
        response = {'status': StatusCodes['internal_error'], 'errors': 'Rank inválido (0-5)'}
        return jsonify(response)
    try:
        Valor = (payload["rating"],payload["feedback"],CodigoProduto)

        cur.execute('insert into rating(rank,feedback,produto_codigobarras) values(%s,%s,%s)',Valor)
        cur.execute(
            'insert into rating_comprador(rating_produto_codigobarras,comprador_user_id_user)values(%s,%s)',(CodigoProduto,id_user))
        cur.execute('commit')
        response = {'status': StatusCodes['success'], 'results': f'Inserted Rating'}


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /rating/<id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)
########################################################################################################################
##########################        PERGUNTAS          ###################################################################
########################################################################################################################

@app.route('/question/<id>', methods=['POST'])
@token_required
def Perguntas(id_user,id):

    logger.info('POST /question')
    payload = request.get_json()
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('select codigobarras from produto where id_produto=%s and versao=true',str(id))
    if(id_user != -1):
        if(cur.rowcount == 0):
            response = {'status': StatusCodes['internal_error'], 'errors': "Não existe nenhum produto com esse ID"}
            return jsonify(response)
    else:
        response = {'status': StatusCodes['success'], 'results': 'Token inexistente'}
        return jsonify(response)


    try:
        cur.execute('select max(id_comentario) from pergunta')
        row = cur.fetchall()
        if(row[0][0]==None):
            ID = 1
        else:
            ID = row[0][0] + 1

        valor = (ID,str(payload["pergunta"]),id_user,id)
        print('insert into pergunta(id_comentario,pergunta,user_id_user,produto_id_produto)values(%s,%s,%s,%s)',valor)
        cur.execute('insert into pergunta(id_comentario,pergunta,user_id_user,produto_id_produto)values(%s,%s,%s,%s)',valor)
        cur.execute('commit')
        response = {'status': StatusCodes['success'], 'results': f'Inserted Question'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /question/<id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)


########################################################################################################################
##########################        RESPOSTAS          ###################################################################
########################################################################################################################
@app.route('/question/<id>/<parent_question_id>', methods=['POST'])
@token_required
def Respostas(id_user,id,parent_question_id):

    logger.info('POST /question/<id>/<parent_question_id>')
    payload = request.get_json()
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('select codigobarras from produto where id_produto=%s and versao=true',str(id))
    if(id_user != -1):
        if(cur.rowcount == 0):
            response = {'status': StatusCodes['internal_error'], 'errors': "Não existe nenhum produto com esse ID"}
            return jsonify(response)

    else:
        response = {'status': StatusCodes['success'], 'results': 'Token inexistente'}
        return jsonify(response)

    cur.execute('select count(*) from pergunta where id_comentario=%s',str(parent_question_id))
    row = cur.fetchall()
    if(row[0][0] == 0):
        response = {'status': StatusCodes['internal_error'], 'errors': "Não existe nenhuma pergunta com esse ParentID"}
        return jsonify(response)
    cur.execute('select count(*) from pergunta where id_comentario=%s and produto_id_produto=%s',(parent_question_id,id,))
    row = cur.fetchall()
    if (row[0][0] == 0):
        response = {'status': StatusCodes['internal_error'], 'errors': "Não existe nenhuma pergunta com esse ParentID com ligação ao Produto!"}
        return jsonify(response)


    try:
        cur.execute('select max(id_comentario) from pergunta')
        row = cur.fetchall()
        if(row[0][0]==None):
            ID = 1
        else:
            ID = row[0][0] + 1

        valor = (ID,str(payload["pergunta"]),id_user,id)

        cur.execute('insert into pergunta(id_comentario,pergunta,user_id_user,produto_id_produto)values(%s,%s,%s,%s)',valor)
        cur.execute('insert into resposta(id_pergunta,id_resposta)values(%s,%s)',(parent_question_id,ID,))
        cur.execute('commit')
        response = {'status': StatusCodes['success'], 'results': f'Inserted Answer'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /question/<id>/<parent_question_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)

########################################################################################################################
##########################        ESTATISTICAS          ###################################################################
########################################################################################################################


@app.route('/report/year', methods=['GET'])
@token_required
def Estatisticas(id_user):

    logger.info('GET /report/year')

    conn = connect_db()
    cur = conn.cursor()
    cur.execute('select * from utilizador where id_user=%s',(id_user,))
    if (id_user != -1):
        if (cur.rowcount == 0):
            response = {'status': StatusCodes['internal_error'], 'errors': "Não existe esse utilizador"}
            return jsonify(response)

    else:
        response = {'status': StatusCodes['success'], 'results': 'Token inexistente'}
        return jsonify(response)
    try:
        cur.execute('''select count(n_compra),sum(encomenda.preco_total),date_part('month',AGE(now(),cast(dataCompra as DATE))) AS mes,date_part('years',AGE(now(),cast(dataCompra as DATE)))*12 AS ano from encomenda
where date_part('years',AGE(now(),cast(dataCompra as DATE)))*12+ date_part('month',AGE(now(),cast(dataCompra as DATE)))< 12
group by ano,mes
Order by ano,mes

''')
        rows = cur.fetchall()

        Results = []
        for row in rows:

            content = {'Mês':int(row[2]), 'total_value': row[1], 'Nª de Orders': row[0]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}
        cur.execute('commit')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /report/year - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)


@app.route('/product/<id>', methods=['GET'])
@token_required
def Informacoes(id_user,id):
    logger.info('GET /product/<id>')
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('select * from produto where id_produto=%s',(id,))
    if(id_user != -1):
        if (cur.rowcount == 0):
            response = {'status': StatusCodes['internal_error'], 'errors': "Não existe nenhum produto com esse ID"}
            return jsonify(response)

    else:
        response = {'status': StatusCodes['success'], 'results': 'Token inexistente'}
        return jsonify(response)
    try:
        cur.execute('''select nome, stock,(select array_agg(pergunta) from pergunta where produto_id_produto=%s
                        group by produto_id_produto) as Perguntas, (select array_agg(codigobarras) from produto where id_produto=%s
                        group by id_produto), (select array_agg(preco) from produto where id_produto=%s group by id_produto) as preco,(select avg(rank) from rating 
                        where produto_codigobarras=(select codigobarras from produto where id_produto=%s))  from produto where codigobarras=(select codigobarras from produto where id_produto=%s and versao is true)
			
''',(str(id),id,id,id,id,))
        rows = cur.fetchall()

        lista = []

        for i in range(len(rows[0][3])):
            auxiliar = str(rows[0][3][i]) + ' - ' +str(rows[0][4][i])

            lista.append(auxiliar)
        content = {'Nome':rows[0][0], 'Stock': rows[0][1], 'Preco': lista,'Comments':rows[0][2],'rating':rows[0][5]}


        response = {'status': StatusCodes['success'], 'results': content}
        cur.execute('commit')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /product/<id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)


@app.route('/Notificacoes/', methods=['GET'])
@token_required
def Notificacoes(id_user):
    logger.info('GET /Notificacoes')

    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute('select informacao from notificacoes where id_user=%s', (id_user,))
        if(cur.rowcount == 0):
            response = {'status': StatusCodes['success'], 'results': 'Não possui notificações!'}
        else:
            rows = cur.fetchall()
            Result = []
            for row in rows:

                Result.append(row[0])

            response = {'status': StatusCodes['success'], 'results': Result}
            cur.execute('commit')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /Notificacoes/ - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)

@app.route('/InfoPergunta/', methods=['GET'])
@token_required
def InfoPergunta(id_user):
    logger.info('GET /InfoPergunta/')

    conn = connect_db()
    cur = conn.cursor()


    if (id_user == -1):

        response = {'status': StatusCodes['success'], 'results': 'Token inexistente'}
        return jsonify(response)

    try:
        cur.execute('select id_comentario,pergunta,produto_id_produto from pergunta')
        if(cur.rowcount == 0):
            response = {'status': StatusCodes['success'], 'results': 'Não possui perguntas!'}
        else:
            rows = cur.fetchall()
            Results = []
            for row in rows:
                logger.debug(row)
                content = {'id_comentario': row[0], 'pergunta': row[1], 'IDproduto': row[2]}
                Results.append(content)
            response = {'status': StatusCodes['success'], 'results': Results}
            cur.execute('commit')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /InfoPergunta/ - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)


if __name__ == '__main__':
    # set up logging
    if(len(sys.argv)!=6):
        print("ERRO NA LINHA DE COMANDO\n")
        exit(-1)
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.1 online: http://{host}:{port}')