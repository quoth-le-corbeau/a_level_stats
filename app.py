from flask import Flask, render_template, request
from typing import Tuple, List, Optional

import processor

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", title="Home")


@app.route("/mean")
def mean():
    return render_template("mean.html", title="Central Tendency")


@app.route("/mean-form", methods=["POST"])
def mean_form():
    data_list, dp, error = _discreet_data_from_form()
    if error is not None:
        return render_template("error.html", data=error[0], error=error[1])
    measures = processor.get_central_tendency(data_list=data_list, dp=dp)
    return render_template("mean-form.html", measures=measures, data=data_list)


def _discreet_data_from_form() -> Tuple[List[float], int, Optional[Tuple[str, str]]]:
    error = None
    data_list = []
    accuracy = request.form.get("accuracy", "2dp")
    if "dp" in accuracy:
        dp = int(accuracy[0])
    else:
        # TODO: handle sig figs
        dp = 6
    data = request.form.get("data", "")
    if data == "":
        error = (data, "Make sure to enter data separated by commas e.g 1.1, 2.2, 3")
    try:
        data_list = list(map(lambda x: float(x), data.split(",")))
    except ValueError:
        error = (
            data,
            "Please only enter numbers using '.' for decimal point. "
            "It could be an unwanted character or maybe you used ',' "
            "as a decimal marker?",
        )
    return data_list, dp, error


@app.route("/spread")
def spread():
    return render_template("spread.html", title="Spread")


@app.route("/spread-form", methods=["POST"])
def spread_form():
    data_list, dp, error = _discreet_data_from_form()
    if error is not None:
        return render_template("error.html", data=error[0], error=error[1])
    measures = processor.get_spread(data_list=data_list, dp=dp)
    return render_template("spread-form.html", measures=measures, data=data_list)


@app.route("/binomial")
def binomial():
    return render_template("binomial.html", title="Binomial")


@app.route("/binomial-form", methods=["POST"])
def binomial_form():
    # accuracy = request.form.get("accuracy", "2dp")

    distribution = request.form.get("distribution", "bcd")
    trials = request.form.get("trials", "")
    probability = request.form.get("probability", "")
    successes = request.form.get("successes", "")
    return render_template(
        "binomial-form.html",
        distribution=distribution,
        trials=trials,
        probability=probability,
        successes=successes,
    )


@app.route("/normal")
def normal():
    return render_template("normal.html", title="Normal")


if __name__ == "__main__":
    app.run(debug=True)
