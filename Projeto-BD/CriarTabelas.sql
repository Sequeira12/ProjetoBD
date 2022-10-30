CREATE TABLE produto (
	id_produto		 BIGINT,
	nome			 VARCHAR(512) NOT NULL,
	preco		 INTEGER NOT NULL,
	marca		 VARCHAR(512) NOT NULL,
	peso			 INTEGER NOT NULL,
	stock		 INTEGER NOT NULL,
	codigobarras		 VARCHAR(512) UNIQUE NOT NULL,
	versao		 BOOL NOT NULL,
	vendedor_user_id_user BIGINT NOT NULL,
	PRIMARY KEY(codigobarras)
);

CREATE TABLE computador (
	ram			 VARCHAR(512) NOT NULL,
	processador		 VARCHAR(512) NOT NULL,
	bateria		 VARCHAR(512) NOT NULL,
	ecra		 VARCHAR(512) NOT NULL,
	produto_codigobarras VARCHAR(512) NOT NULL,
	PRIMARY KEY(produto_codigobarras)
);

CREATE TABLE tv (
	definicao		 VARCHAR(512) NOT NULL,
	smartv		 BOOL NOT NULL,
	dimensao_		 VARCHAR(512) NOT NULL,
	produto_codigobarras VARCHAR(512) NOT NULL,
	PRIMARY KEY(produto_codigobarras)
);

CREATE TABLE smartphone (
	memoria		 VARCHAR(512) NOT NULL,
	resolucao_camara	 VARCHAR(512) NOT NULL,
	bateria		 VARCHAR(512) NOT NULL,
	processador		 BOOL NOT NULL,
	ecra		 VARCHAR(512) NOT NULL,
	produto_codigobarras VARCHAR(512) NOT NULL,
	PRIMARY KEY(produto_codigobarras)
);

CREATE TABLE utilizador (
	id_user	 serial,
	username VARCHAR(512) NOT NULL,
	password VARCHAR(512) NOT NULL,
	email	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(id_user)
);

CREATE TABLE admin (
	name	 VARCHAR(512) NOT NULL,
	anodeservico INTEGER NOT NULL,
	salario	 INTEGER NOT NULL,
	user_id_user BIGINT,
	PRIMARY KEY(user_id_user)
);

CREATE TABLE vendedor (
	name_vend	 VARCHAR(512) NOT NULL,
	nif		 BIGINT NOT NULL,
	morada_envio VARCHAR(512) NOT NULL,
	aprovacao	 BOOL NOT NULL,
	user_id_user BIGINT,
	PRIMARY KEY(user_id_user)
);

CREATE TABLE comprador (
	name_comp	 VARCHAR(512) NOT NULL,
	nif_comp	 BIGINT NOT NULL,
	morada	 VARCHAR(512) NOT NULL,
	n_cartao	 VARCHAR(512) NOT NULL,
	user_id_user BIGINT,
	PRIMARY KEY(user_id_user)
);

CREATE TABLE rating (
	rank		 INTEGER NOT NULL,
	feedback		 VARCHAR(512) NOT NULL,
	produto_codigobarras VARCHAR(512) NOT NULL

);

CREATE TABLE encomenda (
	n_compra		 BIGINT,
	dataCompra timestamp,
	preco_total		 INTEGER NOT NULL,
	comprador_user_id_user BIGINT NOT NULL,
	PRIMARY KEY(n_compra)
);

CREATE TABLE pergunta (
	id_comentario	 BIGINT UNIQUE,
	pergunta		 VARCHAR(512) NOT NULL,
	user_id_user	 BIGINT NOT NULL,
	produto_id_produto BIGINT NOT NULL,
	PRIMARY KEY(id_comentario)
);

CREATE TABLE par_prod_quant (
	quantidade		 INTEGER NOT NULL,
	produto_codigobarras VARCHAR(512) NOT NULL,
	encomenda_n_compra	 BIGINT NOT NULL
);


CREATE TABLE resposta (
    id_pergunta        bigint not NULL,
    id_resposta           bigint not NULL
);

CREATE TABLE rating_comprador (
	rating_produto_codigobarras VARCHAR(512),
	comprador_user_id_user	 BIGINT NOT NULL,
	PRIMARY KEY(rating_produto_codigobarras)
);

CREATE TABLE notificacoes (
    informacao         VARCHAR(512) not NULL,
    data_envio         date NOT NULL,
    id_user BIGINT NOT NULL
);

ALTER TABLE notificacoes ADD CONSTRAINT notificacoes_fk1 FOREIGN KEY (id_user) REFERENCES utilizador(id_user); 

ALTER TABLE produto ADD CONSTRAINT produto_fk1 FOREIGN KEY (vendedor_user_id_user) REFERENCES vendedor(user_id_user);
ALTER TABLE computador ADD CONSTRAINT computador_fk1 FOREIGN KEY (produto_codigobarras) REFERENCES produto(codigobarras);
ALTER TABLE tv ADD CONSTRAINT tv_fk1 FOREIGN KEY (produto_codigobarras) REFERENCES produto(codigobarras);
ALTER TABLE smartphone ADD CONSTRAINT smartphone_fk1 FOREIGN KEY (produto_codigobarras) REFERENCES produto(codigobarras);
ALTER TABLE admin ADD CONSTRAINT admin_fk1 FOREIGN KEY (user_id_user) REFERENCES utilizador(id_user);
ALTER TABLE vendedor ADD CONSTRAINT vendedor_fk1 FOREIGN KEY (user_id_user) REFERENCES utilizador(id_user);
ALTER TABLE comprador ADD CONSTRAINT comprador_fk1 FOREIGN KEY (user_id_user) REFERENCES utilizador(id_user);
ALTER TABLE rating ADD CONSTRAINT rating_fk1 FOREIGN KEY (produto_codigobarras) REFERENCES produto(codigobarras);
ALTER TABLE encomenda ADD CONSTRAINT encomenda_fk1 FOREIGN KEY (comprador_user_id_user) REFERENCES comprador(user_id_user);
ALTER TABLE pergunta ADD CONSTRAINT pergunta_fk1 FOREIGN KEY (user_id_user) REFERENCES utilizador(id_user);
--ALTER TABLE pergunta ADD CONSTRAINT pergunta_fk2 FOREIGN KEY (produto_codigobarras) REFERENCES produto(codigobarras);

ALTER TABLE par_prod_quant ADD CONSTRAINT par_prod_quant_fk2 FOREIGN KEY (encomenda_n_compra) REFERENCES encomenda(n_compra);

ALTER TABLE rating_comprador ADD CONSTRAINT rating_comprador_fk2 FOREIGN KEY (comprador_user_id_user) REFERENCES comprador(user_id_user);

ALTER TABLE resposta ADD CONSTRAINT resposta_fk1 FOREIGN KEY (id_pergunta) REFERENCES pergunta(id_comentario);
ALTER TABLE resposta ADD CONSTRAINT resposta_fk2 FOREIGN KEY (id_resposta) REFERENCES pergunta(id_comentario); 
