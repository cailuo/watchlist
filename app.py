from flask import Flask, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import os, sys

app = Flask(__name__)

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] =  prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
db = SQLAlchemy(app) # 初始化扩展，传入程序实例app

# 创建两个模型类来表示两张数据表
class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

# 创建数据库
import click
@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):  #默认情况下，函数名称就是命令的名字
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

@app.route('/cailuo')
def hello():
    return '<h1>Hello Cailuo!</h1><img src="http://helloflask.com/totoro.gif">'

# @app.route('/user/<name>')
# def user_page(name):
#     return 'User %s' % name
#
# @app.route('/test')
# def test_url_for():
#     print(url_for('hello'))
#     print(url_for('user_page', name='cailuo'))
#     print(url_for('user_page', name='peter'))
#     print(url_for('test_url_for'))
#     print(url_for('test_url_for', num=2))
#     return 'Test page'

name = 'cailuo'


# 向数据库添加虚拟数据
@app.cli.command()
def forge():
    db.create_all()
    name = 'cailuo'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done.')


@app.route('/')
def index():
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)

