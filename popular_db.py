from app.database import SessionLocal
from app.models import ProdutoDB

db = SessionLocal()


db.query(ProdutoDB).delete()
db.commit()


produtos = [
    ProdutoDB(
        nome="Smash Cheaddar",
        preco=24.9,
        imagem="http://10.0.2.2:8000/static/images/bacon_smash.png",
        descricao="Hambúrguer com carne smash, queijo cheddar e molho da casa",
        avaliacao=4.8,
        ingredientes=["pao brioche", "carne smash", "queijo cheddar", "molho especial"],
        categoria="Hamburguers"
    ),
    ProdutoDB(
        nome="Smash Duplo",
        preco=32.0,
        imagem="http://10.0.2.2:8000/static/images/Duplo_smash.png",
        descricao="Hambúrguer duplo com queijo e bacon crocante",
        avaliacao=4.9,
        ingredientes=["pao brioche", "carne smash dupla", "queijo cheddar", "bacon"],
        categoria="Hamburguers"
    ),
    ProdutoDB(
        nome="Sprite Lata",
        preco=6.0,
        imagem="http://10.0.2.2:8000/static/images/sprite_zero.png",
        descricao=" lata 350ml",
        avaliacao=4.5,
        ingredientes=["agua gaseificada", "acucar", "aroma natural"],
        categoria="Bebida"
    ),
    ProdutoDB(
        nome="Suco de Laranja",
        preco=8.5,
        imagem="http://10.0.2.2:8000/static/images/suco_laranja.png",
        descricao="Suco de laranja natural 300ml",
        avaliacao=4.7,
        ingredientes=["laranja fresca"],
        categoria="Bebida"
    ),
    ProdutoDB(
        nome="Brownie",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/brownie.png",
        descricao="Brownie de chocolate com pedaços de nozes",
        avaliacao=4.9,
        ingredientes=["chocolate", "farinha", "acucar", "nozes"],
        categoria="Sobremesa"
    ),
        ProdutoDB(
        nome="Maionese ",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/maionese_temp.png",
        descricao="Maionese da casa",
        avaliacao=4.9,
        ingredientes=["Verduras", "Oleo", "Sal", "Ovos"],
        categoria="Adicionais"
    ),
     ProdutoDB(
        nome="Coca Cola Lata",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/coca.png",
        descricao="Coca Cola Lata",
        avaliacao=4.9,
        ingredientes=["Caramelo", "Agua mineral Gasificada", "Açucar "],
        categoria="Bebida"
    ),
     ProdutoDB(
        nome="Fanta Lata",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/fanta_lata.png",
        descricao="Fanta Lata",
        avaliacao=4.9,
        ingredientes=["Caramelo", "Agua mineral Gasificada", "Açucar "],
        categoria="Bebida"
    ),
     ProdutoDB(
        nome="Fanta Maracuja",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/fanta_maracuja.png",
        descricao="Fanta Maracuja",
        avaliacao=4.9,
        ingredientes=["Maracujá"],
        categoria="Bebida"
    ),
     ProdutoDB(
        nome="Fanta Uva",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/fantauva.png",
        descricao="Fanta Uva",
        avaliacao=4.9,
        ingredientes=["Verduras", "Oleo", "Sal", "Ovos"],
        categoria="Bebida"
    ),
     ProdutoDB(
        nome="Guarana Antartica",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/guarana.png",
        descricao="Guarana Antartica",
        avaliacao=4.9,
        ingredientes=["Verduras", "Oleo", "Sal", "Ovos"],
        categoria="Bebida"
    ),
     ProdutoDB(
        nome="Suco de Acerola",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/acerola_suco.png",
        descricao="Suco de Acerola",
        avaliacao=4.9,
        ingredientes=["Acerola",],
        categoria="Bebida"
    ),
        ProdutoDB(
        nome="Smash 3 Queijos",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/x_queijo.png",
        descricao="Smash 3 Queijos",
        avaliacao=4.9,
        ingredientes=["pao brioche", "carne smash", "queijo cheddar", "molho especial"],
        categoria="Hamburguers"
    ),
        ProdutoDB(
        nome="Smash Frango",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/xfrango.png",
        descricao="Smash Frango",
        avaliacao=4.9,
        ingredientes=["pao brioche", "carne smash", "queijo cheddar", "molho especial"],
        categoria="Hamburguers"
    ),
        ProdutoDB(
        nome="  Smash Milho Cremoso",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/xmilho.png",
        descricao="Smash Milho Cremoso",
        avaliacao=4.9,
        ingredientes=["pao brioche", "carne smash", "queijo cheddar", "molho especial"],
        categoria="Hamburguers"
    ),
     ProdutoDB(
        nome="Smash Ignorante",
        preco=12.0,
        imagem="http://10.0.2.2:8000/static/images/xtudo.png",
        descricao="Smash xTudão",
        avaliacao=4.9,
        ingredientes=["pao brioche", "carne smash", "queijo cheddar", "molho especial"],
        categoria="Hamburguers"
    ),


]

db.add_all(produtos)
db.commit()
db.close()

print("Produtos inseridos com sucesso!")
