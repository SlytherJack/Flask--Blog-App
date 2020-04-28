from flask import Flask, render_template
app = Flask(__name__)

posts = [
    {
        'title': 'My first blog post',
        'author': 'Pradeep Vig',
        'date_posted': '28 Apr 2020',
        'content': 'This is a sample post'
    }
]

@app.route('/')
@app.route('/home')
def hello_world():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return '<h1>About Page</h1>'

# If this file is not imported in some other module
if __name__ == '__main__':
    app.run(debug=True)
