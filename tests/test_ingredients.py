from unittest.mock import patch

from web.models.product import Product


@patch("web.ingredients.retrieve_hierarchy")
@patch("web.ingredients.retrieve_stopwords")
def test_ingredient_query(stopwords, hierarchy, client):
    stopwords.return_value = []
    hierarchy.return_value = [
        Product(id="onion", name="onion", frequency=10),
        Product(id="baked_bean", name="baked bean"),
        Product(id="bean", name="bean", frequency=20),
        Product(id="tofu", name="tofu", frequency=20),
        Product(id="firm_tofu", name="firm tofu"),
        Product(id="jalapeno", name="jalapeño", frequency=5),
        Product(id="soft_tofu", name="soft tofu"),
        Product(id="soy_milk", name="soy milk", frequency=5),
        Product(id="red_bell_pepper", name="red bell pepper", frequency=5),
    ]

    expected_results = {
        "large onion, diced": {
            "markup": "large <mark>onion</mark>, diced",
            "product": "onion",
            "product_id": "onion",
        },
        "can of Baked Beans": {
            "markup": "can of <mark>Baked Beans</mark>",
            "product": "baked beans",
            "product_id": "baked_bean",
        },
        "block of firm tofu": {
            "markup": "block of <mark>firm tofu</mark>",
            "product": "firm tofu",
            "product_id": "firm_tofu",
        },
        "block tofu": {
            "markup": "block <mark>tofu</mark>",
            "product": "tofu",
            "product_id": "tofu",
        },
        "pressed soft tofu": {
            "markup": "pressed <mark>soft tofu</mark>",
            "product": "soft tofu",
            "product_id": "soft_tofu",
        },
        "soy milk": {
            "markup": "<mark>soy milk</mark>",
            "product": "soy milk",
            "product_id": "soy_milk",
        },
        "250ml of soy milk (roughly one cup)": {
            "markup": "250ml of <mark>soy milk</mark> (roughly one cup)",
            "product": "soy milk",
            "product_id": "soy_milk",
        },
        "Sliced red bell pepper, as filling": {
            "markup": "Sliced <mark>red bell pepper</mark>, as filling",
            "product": "red bell pepper",
            "product_id": "red_bell_pepper",
        },
        "jalapeño pepper": {
            "markup": "<mark>jalapeño</mark> pepper",
            "product": "jalapeño",
            "product_id": "jalapeno",
        },
        "tofu (soft tofu or silken tofu is best)": {
            "markup": "<mark>tofu</mark> (soft tofu or silken tofu is best)",
            "product": "tofu",
            "product_id": "tofu",
        },
    }

    results = client.post(
        "/ingredients/query", data={"descriptions[]": list(expected_results.keys())}
    ).json["results"]

    for query, expected in expected_results.items():
        assert results[query]["product"]["id"] == expected["product_id"]
        assert results[query]["product"]["product"] == expected["product"]
        assert results[query]["query"]["markup"] == expected["markup"]
