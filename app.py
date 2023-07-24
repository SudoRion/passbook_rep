from flask import Flask, request, redirect, render_template, url_for
from math import ceil
import sqlite3

app = Flask(__name__, static_folder="static")


def get_db():
    db = sqlite3.connect("account.db")
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with app.app_context():
        try:
            db = get_db()

        finally:
            db.close()


init_db()


@app.route("/", methods=["GET", "POST"])
def addtask():
    try:
        db = get_db()
        page = int(request.args.get("page", 1))
        items_per_page = 10

        with db:
            account = db.execute(
                "SELECT * FROM account ORDER BY id DESC LIMIT ? OFFSET ?", (items_per_page, (page - 1) * items_per_page)
            ).fetchall()
            total_items = db.execute("SELECT COUNT(*) FROM account").fetchone()[0]
            total_pages = ceil(total_items / items_per_page)

        if request.method == "POST":
            text = request.form["text"]
            amount = request.form["amount"]
            date = request.form["date"]
            payWhich = request.form["pay_which"]

            get_amount = 0
            pay_amount = 0

            if payWhich == "+":
                get_amount = int(amount)
            else:
                pay_amount -= int(amount)

            last_sum_amount = db.execute("SELECT sum_amount FROM account ORDER BY id DESC LIMIT 1").fetchone()[
                "sum_amount"
            ]
            sum_amount = last_sum_amount + get_amount - pay_amount

            with db:
                db.execute(
                    "INSERT INTO account (pay_name,amount,get_amount,pay_amount,pay_date,pay_which,sum_amount) VALUES (?,?,?,?,?,?,?)",
                    (text, amount, get_amount, pay_amount, date, payWhich, sum_amount),
                )

            return redirect("/?page=1")

        return render_template("index.html", account=account, page=page, total_pages=total_pages)

    finally:
        db.close()


# @app.route("/", methods=["GET", "POST"])
# def addtask():
#     try:
#         db = get_db()

#         with db:
#             account = db.execute("SELECT * FROM account").fetchall()
#             # sum_month = db.execute("SELECT * FROM sum_month").fetchall()
#             last_amount = db.execute("SELECT sum_amount FROM account ORDER BY id DESC LIMIT 1")

#         if request.method == "POST":
#             text = request.form["text"]
#             amount = request.form["amount"]
#             date = request.form["date"]
#             payWhich = request.form["pay_which"]

#             if payWhich == "+":
#                 last_amount = int(amount)
#             else:
#                 last_amount -= int(amount)

#             # sum_old =
#             # 一つ前のsum_amountを取得、そこにプラスかマイナス
#             with db:
#                 db.execute(
#                     # "INSERT INTO account (pay_name,amount,pay_date) VALUES (?,?,?)",
#                     "INSERT INTO account (pay_name,amount,pay_date,pay_which,sum_amount) VALUES (?,?,?,?,?)",
#                     (
#                         text,
#                         amount,
#                         date,
#                         payWhich,
#                         last_amount,
#                     ),
#                     # "INSERT INTO sum_month (month,sum_month) VALUES(?,?)",
#                     # (
#                     #     month,
#                     #     sum,
#                     # ),
#                 )
#             return redirect("/")

#         return render_template("index.html", account=account)
#     finally:
#         db.close()


@app.route("/edit", methods=["POST"])
def edit():
    if request.method == "POST":
        id = int(request.form["id"])
        update_task = request.form["update_task"]

        try:
            db = get_db()
            with db:
                db.execute(
                    "UPDATE account SET pay_name = ? WHERE id = ?",
                    (update_task, id),
                )
            return redirect("/")
        finally:
            db.close()


@app.route("/graph")
def chart_do():
    c = {
        "chart_labels": "項目1, 項目２, 項目３, 項目４,項目５",
        "chart_data": "4, 7, 8, 5, 6",
        "chart_title": "グラフサンプル",
        "chart_target": "タイトル",
    }
    return render_template("graph.html", c=c)


# ハリパネ：A3
