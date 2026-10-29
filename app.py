import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

from extensions import db
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = "chave-do-projeto"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://Flask_05:12345@localhost/Trabalho05"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

from models import Apresentacao, Palco, Artista, Contrato

migrate = Migrate(app, db)


# Rota Principal - Página Inicial (Listagem em Cards)

@app.route('/')
def index():
    apresentacoes = Apresentacao.query.all()

    return render_template(
        'index.html',
        apresentacoes=apresentacoes
    )


@app.route('/create', methods=['GET', 'POST'])
def create():
    palcos = Palco.query.all()
    artistas = Artista.query.all()

    if request.method == 'POST':
        try:
            artista_id = int(request.form['artista_id'])
            palco_id = int(request.form['palco_id'])

            artista = db.session.get(Artista, artista_id)
            palco = db.session.get(Palco, palco_id)

            if artista is None or palco is None:
                raise ValueError("Selecione um artista e um palco válidos.")

            nova_apresentacao = Apresentacao(
                nome=request.form.get('nome') or artista.nome,
                data=datetime.strptime(
                    request.form['data'], '%Y-%m-%d'
                ).date(),
                hora_inicio=datetime.strptime(
                    request.form['hora_inicio'], '%H:%M'
                ).time(),
                hora_fim=datetime.strptime(
                    request.form['hora_fim'], '%H:%M'
                ).time(),
                artista_id=artista_id,
                palco_id=palco_id
            )

            db.session.add(nova_apresentacao)
            db.session.commit()

            flash('Apresentação cadastrada com sucesso!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            print(f'ERRO AO CADASTRAR: {repr(e)}')
            flash(f'Erro ao cadastrar: {e}', 'danger')

    return render_template(
        'create.html',
        palcos=palcos,
        artistas=artistas
    )

@app.route('/palco/create_palco', methods=['GET', 'POST'])
def create_palco():
    if request.method == 'POST':
        try:
            novo_palco = Palco(
                titulo=request.form['titulo'].strip(),
                localizacao=request.form['localizacao'].strip(),
                capacidade=int(request.form['capacidade'])
            )

            if not novo_palco.titulo or not novo_palco.localizacao:
                raise ValueError("Preencha todos os campos.")

            if novo_palco.capacidade < 1:
                raise ValueError("A capacidade deve ser maior que zero.")

            db.session.add(novo_palco)
            db.session.commit()

            flash('Palco cadastrado com sucesso!', 'success')
            return redirect(url_for('create'))

        except Exception as erro:
            db.session.rollback()
            flash(f'Erro ao cadastrar palco: {erro}', 'danger')

    return render_template('create_palco.html')


@app.route('/artista/create_artista', methods=['GET', 'POST'])
def create_artista():
    if request.method == 'POST':
        try:
            nome = request.form['nome'].strip()

            if not nome:
                raise ValueError("Informe o nome do artista.")

            novo_artista = Artista(nome=nome)

            db.session.add(novo_artista)
            db.session.commit()

            flash('Artista cadastrado com sucesso!', 'success')
            return redirect(url_for('create'))

        except Exception as erro:
            db.session.rollback()
            flash(f'Erro ao cadastrar artista: {erro}', 'danger')

    return render_template('create_artista.html')



# Editar Apresentação
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    apresentacao = db.get_or_404(Apresentacao, id)
    palcos = Palco.query.all()
    artistas = Artista.query.all()

    if request.method == "POST":
        try:
            apresentacao.nome = request.form["nome"]
            apresentacao.data = datetime.strptime(request.form["data"], "%Y-%m-%d").date()
            apresentacao.hora_inicio = datetime.strptime(request.form["hora_inicio"], "%H:%M").time()
            apresentacao.hora_fim = datetime.strptime(request.form["hora_fim"], "%H:%M").time()
            apresentacao.artista_id = int(request.form["artista_id"])
            apresentacao.palco_id = int(request.form["palco_id"])

            db.session.commit()
            flash("Apresentação atualizada com sucesso!")
            return redirect(url_for("index"))

        except Exception as erro:
            db.session.rollback()
            flash(f"Erro ao atualizar: {erro}")

    return render_template("update.html", apresentacao=apresentacao, palcos=palcos, artistas=artistas)


# Eliminar Apresentação

# Excluir uma apresentação
@app.route('/delete_apresentacao/<int:id>', methods=['POST'])
def delete_apresentacao(id):
    apresentacao = db.session.get(Apresentacao, id)

    if apresentacao is None:
        flash('Apresentação não encontrada.', 'danger')
    else:
        db.session.delete(apresentacao)
        db.session.commit()
        flash('Apresentação excluída com sucesso!', 'success')

    return redirect(url_for('index'))


# Excluir um palco e suas apresentações
@app.route('/delete_palco/<int:id>', methods=['POST'])
def delete_palco(id):
    palco = db.session.get(Palco, id)

    if palco is None:
        flash('Palco não encontrado.', 'danger')
    else:
        try:
            # Remove primeiro as apresentações desse palco
            Apresentacao.query.filter_by(palco_id=id).delete(
                synchronize_session=False
            )

            db.session.delete(palco)
            db.session.commit()
            flash('Palco e suas apresentações excluídos!', 'success')

        except Exception as erro:
            db.session.rollback()
            flash(f'Erro ao excluir palco: {erro}', 'danger')

    return redirect(url_for('index'))


# Excluir um artista, suas apresentações e seu contrato
@app.route('/delete_artista/<int:id>', methods=['POST'])
def delete_artista(id):
    artista = db.session.get(Artista, id)

    if artista is None:
        flash('Artista não encontrado.', 'danger')
    else:
        try:
            # Remove as apresentações desse artista
            Apresentacao.query.filter_by(artista_id=id).delete(
                synchronize_session=False
            )

            # Remove o contrato, caso exista
            contrato = Contrato.query.filter_by(artista_id=id).first()

            if contrato is not None:
                db.session.delete(contrato)

            db.session.delete(artista)
            db.session.commit()
            flash('Artista, suas apresentações e seu contrato foram excluídos!', 'success')

        except Exception as erro:
            db.session.rollback()
            flash(f'Erro ao excluir artista: {erro}', 'danger')

    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)