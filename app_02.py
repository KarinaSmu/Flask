from flask import Flask, render_template, request, redirect, make_response

app = Flask(__name__)
app.secret_key = 'd47cec15d3866500bd20f5aae44c06aa'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/welcome', methods=['POST'])
def welcome():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        response = make_response(redirect('/greet'))
        response.set_cookie('user_name', name)
        response.set_cookie('user_email', email)
        return response


@app.route('/greet')
def greet():
    user_name = request.cookies.get('user_name')

    if user_name is None:
        return redirect('/')

    return render_template('greet.html', user_name=user_name)


@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.delete_cookie('user_name')
    response.delete_cookie('user_email')
    return response


if __name__ == '__main__':
    app.run(debug=True)
