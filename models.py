from extensions import db

class Palco(db.Model):
    __tablename__ = 'palcos'

    palco_id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    localizacao = db.Column(db.String(150), nullable=False)
    capacidade = db.Column(db.Integer, nullable=False)

    apresentacoes = db.relationship('Apresentacao', back_populates='palco')


class Artista(db.Model):
    __tablename__ = 'artistas'

    artista_id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))

    apresentacoes = db.relationship('Apresentacao', back_populates='artista')
    contrato = db.relationship('Contrato', back_populates='artista', uselist=False)


class Contrato(db.Model):
    __tablename__ = 'contratos'

    id = db.Column(db.Integer, primary_key=True)
    artista_id = db.Column(db.Integer, db.ForeignKey('artistas.artista_id'), nullable=False, unique=True)
    cache = db.Column(db.Float, nullable=False)
    data_assinatura = db.Column(db.Date, nullable=False)

    artista = db.relationship('Artista', back_populates='contrato')


class Apresentacao(db.Model):
    __tablename__ = 'apresentacoes'

    apresentacao_id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)

    artista_id = db.Column(db.Integer, db.ForeignKey('artistas.artista_id'), nullable=False)
    palco_id = db.Column(db.Integer, db.ForeignKey('palcos.palco_id'), nullable=False)

    artista = db.relationship('Artista', back_populates='apresentacoes')
    palco = db.relationship('Palco', back_populates='apresentacoes')