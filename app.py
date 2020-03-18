from flask import Flask, url_for, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os, sys

app = Flask(__name__)
# 设置签名所需的密钥
app.config['SECRET_KEY'] = 'dev'   # 等同于 app.secret_key = 'dev'

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


# 向数据库添加数据
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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')   # 表单字段的name值
        year = request.form.get('year')     # 表单字段的name值
        if not title or not year or len(year) > 4 or len(title) > 60:
            # get_flashed_messages()函数用来在模板中获取提示信息
            flash('Invalid input.')      # 显示错误提示
            return redirect(url_for('index'))       # 重定向回主页
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created')   # 显示创建成功的提示
        return redirect(url_for('index'))

    # user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


@app.errorhandler(404)
def page_not_found(e):
    # user = User.query.first()
    return render_template('404.html'), 404

# 对于多个模板内都需要使用的变量，我们可以使用 app.context_processor 装
# 饰器注册一个模板上下文处理函数
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)  # 需要返回字典
# 这个函数返回的变量（以字典键值对的形式） 将会统一注入到每一个模板的上下文
# 环境中，因此可以直接在模板中使用

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/form')
def form():
    return render_template('form.html')

# 编辑电影条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    # get_or_404: 会返回对应主键的记录(返回的是记录)，如果没有找到，则返回404错误响应
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


# 删除条目
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))




