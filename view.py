from flask import Blueprint, render_template, request, flash, redirect, abort
from flask_login import login_required, current_user
from data import db_session
from forms.news import NewsForm
from data.news import News
from find_toxicity import find_toxicity

view = Blueprint("view", __name__)


@view.route("/", methods=["GET", "POST"])
@login_required
def homepage():
    toxic = 0.00
    comment = ""
    if request.method == "POST":
        comment = request.form.get("comment")
        score = find_toxicity(comment)
        toxic = round(score[0][0] * 100, 2)
    return render_template("home.html", user=current_user, toxic=toxic, comment=comment)


@view.route("/news")
@login_required
def news_check():
    # функция для показа новостей пользователям
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != 1))
    else:
        news = db_sess.query(News).filter(News.is_private != 1)
    return render_template("news.html", news=news, user=current_user)


@view.route("/news-add", methods=["GET", "POST"])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        db_sess = db_session.create_session()
        current_user.news.append(news)
        db_sess.merge(current_user)
        score = find_toxicity(form.content.data)
        if round(score[0][0] * 100, 2) > 0.5:
            flash("Ваше сообщение возможно содержит неприемлемый контент и будет добавлено "
                  "только после проверки", "error")
            return redirect("/news")
        db_sess.commit()
        return redirect('/news')
    return render_template('news_action.html', title='Добавление новости',
                           form=form, user=current_user, act="Add news")


@view.route('/edit-news/<int:news_id>', methods=['GET', 'POST'])
@login_required
def edit_news(news_id):
    form = NewsForm()
    if request.method == "GET":
        # переход на страничку изменения новости
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == news_id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        # редактирование новости (метод запроса POST)
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == news_id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            score = find_toxicity(form.content.data)
            if round(score[0][0] * 100, 2) > 0.5:
                flash("Ваше сообщение возможно содержит неприемлемый контент и будет добавлено "
                      "только после проверки", "error")
                return redirect("/news")
            db_sess.commit()
            return redirect('/news')
        else:
            abort(404)
    return render_template('news_action.html',
                           title='Редактирование новости',
                           form=form, user=current_user, act="Edit news"
                           )


@view.route('/news_delete/<int:news_id>', methods=['GET', 'POST'])
@login_required
def news_delete(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/news')
