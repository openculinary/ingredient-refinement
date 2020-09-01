from unittest.mock import patch

from web.app import app
from web.models.product import Product


@patch('web.ingredients.retrieve_hierarchy')
@patch('web.ingredients.retrieve_stopwords')
def test_ingredient_query(stopwords, hierarchy, client):
    # HACK: Ensure that app initialization methods (re)run during this test
    app._got_first_request = False

    stopwords.return_value = []
    hierarchy.return_value = [
        Product(name='onion', frequency=10, parent_id=None),
        Product(name='baked bean', frequency=5, parent_id='bean'),
        Product(name='bean', frequency=20, parent_id=None),
        Product(name='tofu', frequency=20, parent_id=None),
        Product(name='firm tofu', frequency=10, parent_id='tofu'),
        Product(name='jalapeño', frequency=5),
        Product(name='soft tofu', frequency=5, parent_id='tofu'),
        Product(name='soy milk', frequency=5, parent_id=None),
        Product(name='red bell pepper', frequency=5, parent_id=None),
        Product(name='red bell pepper', frequency=5, parent_id=None),
    ]

    expected_results = {
        'large onion, diced': {
            'markup': 'large <mark>onion</mark>, diced',
            'product': 'onion',
            'product_id': 'onion',
        },
        'can of Baked Beans': {
            'markup': 'can of <mark>Baked Beans</mark>',
            'product': 'baked beans',
            'product_id': 'bake_bean',
        },
        'block of firm tofu': {
            'markup': 'block of <mark>firm tofu</mark>',
            'product': 'firm tofu',
            'product_id': 'firm_tofu',
        },
        'block tofu': {
            'markup': 'block <mark>tofu</mark>',
            'product': 'tofu',
            'product_id': 'tofu',
        },
        'pressed soft tofu': {
            'markup': 'pressed <mark>soft tofu</mark>',
            'product': 'soft tofu',
            'product_id': 'soft_tofu',
        },
        'soymilk': {
            'markup': '<mark>soy milk</mark>',
            'product': 'soy milk',
            'product_id': 'milk_soy',
        },
        '250ml of soymilk (roughly one cup)': {
            'markup': '250ml of <mark>soy milk</mark> (roughly one cup)',
            'product': 'soy milk',
            'product_id': 'milk_soy',
        },
        'Sliced red bell pepper, as filling': {
            'markup': 'Sliced <mark>red bell pepper</mark>, as filling',
            'product': 'red bell pepper',
            'product_id': 'bell_pepper_red',
        },
        'jalapeño pepper': {
            'markup': '<mark>jalapeño</mark> pepper',
            'product': 'jalapeño',
            'product_id': 'jalapeno',
        },
    }

    results = client.post(
        '/ingredients/query',
        data={'descriptions[]': list(expected_results.keys())}
    ).json['results']

    for query, expected in expected_results.items():
        assert results[query]['product']['id'] == expected['product_id']
        assert results[query]['product']['product'] == expected['product']
        assert results[query]['query']['markup'] == expected['markup']


@patch('web.ingredients.retrieve_hierarchy')
@patch('web.ingredients.retrieve_stopwords')
def test_nutrition_response(stopwords, hierarchy, client):
    # HACK: Ensure that app initialization methods (re)run during this test
    app._got_first_request = False

    product = 'onion'
    nutrition = {
        'product': product,
        'protein': 1.0,
        'fat': 0.1,
        'carbohydrates': 8.0,
        'energy': 35.0,
        'fibre': 2.0,
    }

    stopwords.return_value = []
    hierarchy.return_value = [
        Product(
            name=product,
            frequency=10,
            parent_id=None,
            nutrition=nutrition,
        )
    ]

    expected_results = {
        'medium onion': {
            'markup': 'medium <mark>onion</mark>',
            'nutrition': nutrition,
        }
    }

    results = client.post(
        '/ingredients/query',
        data={'descriptions[]': list(expected_results.keys())}
    ).json['results']

    for query, expected in expected_results.items():
        del expected['nutrition']['product']
        assert results[query]['query']['markup'] == expected['markup']
        assert results[query]['product']['nutrition'] == expected['nutrition']
