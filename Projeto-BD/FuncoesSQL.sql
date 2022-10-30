create index notifboost
on notificacoes(id_user);

create index respostaboost
on resposta(id_resposta);

CREATE INDEX loginboost
on utilizador (username,password);

create index idprodboost
on produto(id_produto);

create index encomendaboost
on par_prod_quant(encomenda_n_compra);

create or replace function notif_resposta()
returns trigger
language plpgsql
as $$
declare
v_respondido pergunta.user_id_user%type;
v_nome_produto produto.nome%type;
begin
select distinct nome into v_nome_produto from produto
where id_produto=(select produto_id_produto from pergunta where id_comentario=new.id_pergunta);
select user_id_user into v_respondido from pergunta
where id_comentario=new.id_pergunta;
insert into notificacoes (informacao, data_envio,id_user)
values ('A sua pergunta sobre o produto '||v_nome_produto||' foi respondida',current_date,v_respondido);
return NULL;
end;
$$;  

create or replace function notif_vendedor()
returns trigger
language plpgsql
as $$
declare
v_idvendedor utilizador.id_user%type;
begin
select distinct (vendedor_user_id_user) into v_idvendedor
from produto where id_produto=new.produto_id_produto;
insert into notificacoes (informacao,data_envio,id_user)
values ('Foi feito um coment??rios sobre o produto '||new.produto_id_produto ,current_date,v_idvendedor);
return NULL;
end;
$$; 


create or replace function notif_venda()
returns trigger
language plpgsql
as $$
declare
v_idvendedor utilizador.id_user%type;
c_prod_vendidos cursor for select * from
par_prod_quant where encomenda_n_compra=new.n_compra;
begin
insert into notificacoes(informacao,data_envio,id_user)
values ('A sua compra foi realizada com sucesso',CURRENT_DATE,new.comprador_user_id_user);
for r in c_prod_vendidos
loop
select vendedor_user_id_user into v_idvendedor
from produto where codigobarras=r.produto_codigobarras;
insert into notificacoes (informacao,data_envio,id_user)
values('Foi vendido o produto'||r.produto_codigobarras||'Numa quantidade de '||r.quantidade,CURRENT_DATE,v_idvendedor);
end loop;
return NULL;
end;
$$; 

create or replace function compra(v_quant integer, v_codigobarras produto.codigobarras%type,v_encomenda par_prod_quant.encomenda_n_compra%type) 
returns integer
language plpgsql
as $$
--verifica_encomenda
declare 
v_stock integer;
v_valid integer;
begin
select stock into v_stock from produto
where codigobarras=v_codigobarras;
if v_quant > v_stock then
rollback;
v_valid:=0;
return v_valid;
else
update produto set stock=v_stock-v_quant where codigobarras=v_codigobarras;
v_valid:=1;
return v_valid;
end if;
end;
$$; 

Create or replace trigger POS_VENDA after update
on encomenda
for each row
execute function notif_venda(); 

Create or replace trigger NOTIFVENDEDOR after insert
on pergunta
for each row
execute function notif_vendedor(); 

Create or replace trigger NOTIFRESPOSTA after insert
on resposta
for each row
execute function notif_resposta(); 

insert into utilizador(id_user,username,password,email)values(1,'Teste','eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNzd29yZCI6InBhc3NBZG1pbiJ9.D46Ealt4mehAbSq12HYJmq0iNEYF0mMCnly3rS_g95g','admin@email.com');
insert into admin(name,anodeservico,salario,user_id_user)values('Teste',2022,1200,1);

