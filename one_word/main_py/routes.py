from flask import render_template,Blueprint
from one_word.models import User,StoryPost
main = Blueprint('main',__name__)

@main.route('/')
def home():
    users = User.query.all()
    return render_template('home.html',users=users)

@main.route('/read_stories')
def read_stories():
    stories = StoryPost.query.all()
    return render_template('stories.html',stories=stories)

# @main.route('/test')
# def test():
#     return render_template('test.html')
