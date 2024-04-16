from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/category/<category>')
def category(category):
    return render_template('category.html', category=category)

@app.route('/product/<int:product_id>')
def product(product_id):
    product_info = {
        'name': 'Пример товара',
        'price': 100.0,
    }
    return render_template('product.html', product=product_info)

if __name__ == '__main__':
    app.run(debug=True)
