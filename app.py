from flask import Flask, request, redirect, render_template, url_for
from math import ceil
from jinja2 import Template

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
    # 通帳のページ（1枚につき10件表示）
    try:
        db = get_db()
        page = int(request.args.get("page", 1))
        items_per_page = 10

        # ページごとに表示する10件を取得
        with db:
            account = db.execute(
                "SELECT * FROM account ORDER BY id DESC LIMIT ? OFFSET ?", (items_per_page, (page - 1) * items_per_page)
            ).fetchall()
            total_items = db.execute("SELECT COUNT(*) FROM account").fetchone()[0]
            total_pages = ceil(total_items / items_per_page)

            sum_month_table = db.execute("SELECT * FROM sum_month_table").fetchall()

            total_get_amount = 0
            total_pay_amount = 0
            total_get_amount = db.execute("SELECT SUM(get_amount) FROM account").fetchone()
            total_pay_amount = db.execute("SELECT SUM(pay_amount) FROM account").fetchone()

        if request.method == "POST":
            text = request.form["text"]
            amount = request.form["amount"]
            date = request.form["date"]
            payWhich = request.form["pay_which"]
            set_month = request.form["set_month"]

            if text and amount and date and payWhich and set_month:
                get_amount = 0
                pay_amount = 0

                # 支払いか預かりの判断
                if payWhich == "+":
                    get_amount = int(amount)
                else:
                    pay_amount = -int(amount)

                result = last_sum_amount = db.execute(
                    "SELECT sum_amount FROM account ORDER BY id DESC LIMIT 1"
                ).fetchone()
                if result is not None:
                    last_sum_amount = result["sum_amount"]
                else:
                    last_sum_amount = 0

                sum_amount = last_sum_amount + get_amount + pay_amount

                with db:
                    db.execute(
                        "INSERT INTO account (pay_name,amount,get_amount,pay_amount,pay_date,pay_which,sum_amount) VALUES (?,?,?,?,?,?,?)",
                        (text, amount, get_amount, pay_amount, date, payWhich, sum_amount),
                    )

                    current_month = db.execute("SELECT * FROM sum_month_table WHERE month = ?", (set_month,)).fetchone()

                    current_sum_amount = current_month["sum_amount"]
                    if payWhich == "+":
                        updated_sum_amount = current_sum_amount + int(amount)
                    else:
                        updated_sum_amount = current_sum_amount - int(amount)
                    db.execute(
                        "UPDATE sum_month_table SET sum_amount = ? WHERE month = ?", (updated_sum_amount, set_month)
                    )

                return redirect("/?page=1")
            else:
                return redirect("/?page=1")

        return render_template(
            "index.html",
            account=account,
            page=page,
            total_pages=total_pages,
            sum_month_table=sum_month_table,
            total_get_amount=total_get_amount[0],
            total_pay_amount=total_pay_amount[0],
        )

    finally:
        db.close()
