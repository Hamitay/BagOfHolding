import os
import flask

from models.coin import Coin
from models.item import Item

from models import db

app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///bag.db'
db.init_app(app)

app.app_context().push()
db.create_all()

app.secret_key = os.urandom(24)

@app.route("/login", methods = ["POST", "GET"])
def login():
    if flask.request.method == "POST":
        if flask.request.form["user"] == "admin" and flask.request.form["pass"] == "admin":
            flask.session["logged_in"] = True
            return flask.redirect("/")
        else:
            error = "Invalid credentials"
            return flask.render_template("login.html", error=error)

    else:
        return flask.render_template("login.html")

@app.route("/logout")
def logout():
    flask.session["logged_in"] = False
    return flask.redirect("/")

@app.route("/", methods = ["POST", "GET"])
def index():
    if flask.request.method == "POST":
        new_item = Item(flask.request.form["name"],
                        flask.request.form["description"],
                        flask.request.form["location"],
                        flask.request.form["price"],
                        flask.request.form["weight"],
                        flask.request.form["quantity"],
                        flask.request.form["type"],
                        flask.request.form["isMagic"],
                        flask.request.form["href"])

        try:
            db.session.add(new_item)
            db.session.commit()
            return flask.redirect("/")

        except Exception as e:
            raise
    else:
        if flask.session.get("logged_in"):
            items = Item.query.order_by(Item._name).all()
            items_value = _getValue(items)
            items_weight = _getWeight(items)

            coins = Coin.query.order_by(Coin._value).all()
            party_gold = _convertDefault(coins)

            return flask.render_template("index.html",
                                         items=items,
                                         items_value=items_value,
                                         items_weight=items_weight,
                                         party_gold=party_gold)
        else:
            return flask.redirect("/login")

@app.route("/create")
def create_item():
    return flask.render_template("create.html")

@app.route("/delete/<int:id>")
def delete_item(id):
    item = Item.query.get_or_404(id)

    try:
        db.session.delete(item)
        db.session.commit()
        return flask.redirect("/")

    except Exception as e:
        raise

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_item(id):
    item = Item.query.get_or_404(id)

    if flask.request.method == "POST":
        item._name = flask.request.form["name"]
        item._description = flask.request.form["description"]
        item._location = flask.request.form["location"]
        item._price = flask.request.form["price"]
        item._weight = flask.request.form["weight"]
        item._quantity = flask.request.form["quantity"]
        item._type = flask.request.form["type"]
        item._isMagic = flask.request.form["isMagic"]
        item._href = flask.request.form["href"]

        try:
            db.session.commit()
            return flask.redirect("/")
        except Exception as e:
            raise

    else:
        return flask.render_template("update.html", item=item)

@app.route("/copy/<int:id>")
def copy_item(id):
    item = Item.query.get_or_404(id)
    new_item = Item(item._name,
                    item._description,
                    item._location,
                    item._price,
                    item._weight,
                    item._quantity,
                    item._type,
                    item._isMagic,
                    item._href)

    try:
        db.session.add(new_item)
        db.session.commit()
        return flask.redirect("/")

    except Exception as e:
        raise

@app.route("/add/<int:id>")
def add_item(id):
    item = Item.query.get_or_404(id)

    item._quantity += 1

    try:
        db.session.commit()
        return flask.redirect("/")
    except Exception as e:
        raise

@app.route("/subtract/<int:id>")
def subtract(id):
    item = Item.query.get_or_404(id)

    item._quantity -= 1

    try:
        db.session.commit()
        return flask.redirect("/")
    except Exception as e:
        raise

@app.route("/update/coin", methods=["GET", "POST"])
def update_coin():
    coins = Coin.query.order_by(Coin._value).all()

    if flask.request.method == "POST":
        for coin in coins:
            coin_quantity = "{}_quantity".format(coin._name)
            coin._quantity = flask.request.form[coin_quantity]

        try:
            db.session.commit()

            return flask.redirect("/")
        except Exception as e:
            raise

    return flask.render_template("coins.html", coins=coins)

def _getValue(items):
    total_value = 0.0
    for item in items:
        total_value += (item._price * item._quantity)

    return round(total_value, 1)

def _getWeight(items):
    total_weight = 0.0
    for item in items:
        total_weight += (item._weight * item._quantity)

    return round(total_weight, 1)

def _convertDefault(coins, default="Gold"):
    default_value = Coin.query.filter_by(_name=default).first()

    # TODO Make the application stateless
    default_value = default_value._value if default_value else 1

    gold = 0.0
    for coin in coins:
        gold += coin._value * coin._quantity

    return round(gold/default_value, 1)

if __name__ == '__main__':
    app.run(debug=True)