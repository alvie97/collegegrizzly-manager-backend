from app import db
from app.models.question import Question
from app.models.option import Option

url = "/api/questions"


def test_get_questions(app, client, auth):
    """ get all questions and test search function """

    # create questions to test

    questions_properties = []

    with app.app_context():
        for i in range(50):

            questions_properties.append({"name": f"test question {i}"})

            question = Question(**questions_properties[i])
            db.session.add(question)

        db.session.commit()

    # login

    auth.login()

    # get questions

    response = client.get(url)
    data = response.get_json()
    questions = data["items"]

    for i, question in enumerate(questions):
        assert question["name"] == questions_properties[i]["name"]

    # get question that ends with "or 2"

    response = client.get(url + "?search=on 2")
    data = response.get_json()
    questions = data["items"]

    assert len(questions) > 0

    for question in questions:
        assert question["name"].find("on 2") != -1


def test_create_question(app, client, auth):
    """creates question"""

    auth.login()

    # create question

    data = {"name": "test post question"}

    response = client.post(url, json=data)
    response_data = response.get_json()
    question_url = response_data["question"]

    response = client.get(question_url)
    response_data = response.get_json()

    with app.test_request_context():
        question = Question.get(response_data["id"])

        assert question is not None
        assert question.to_dict() == response_data


def test_delete_question(app, client, auth):
    """ create questions and edit them"""

    # delete question
    auth.login()

    with app.app_context():
        question = Question(name="test question")
        db.session.add(question)
        db.session.commit()

        client.delete(url + f"/{question.id}")

        question = Question.get(question.id)

        assert question is None


def test_option_question_relationship(app, questions, options):
    """
    test option and question schema.
    """

    with app.app_context():
        question = Question.query.first()
        options_array = Option.query.limit(5).all()

        for option in options_array:
            question.add_option(option)

        db.session.commit()
        assert question.options.count() == 5

        question.remove_option(options_array[2])
        question.remove_option(options_array[4])

        db.session.commit()

        assert question.options.count() == 3

        for id, option in enumerate(options_array):
            if (id == 2 or id == 4):
                assert not question.has_option(option.id)
            else:
                assert question.has_option(option.id)


def test_api_endpoint_get_options(app, client, auth, questions, options):
    """
    Tests get_options endpoint
    """

    with app.app_context():
        question = Question.query.first()
        options_array = Option.query.limit(5).all()

        for option in options_array:
            question.add_option(option)

        db.session.commit()
        assert question.options.count() == 5

    auth.login()

    response = client.get(url + "/1/options")
    assert response.status_code == 200
    json_response = response.get_json()["items"]

    with app.app_context():
        question = Question.query.first()
        for option in json_response:
            assert question.has_option(option["id"])


def test_add_options(app, client, auth, questions, options):
    """
    Tests add_options endpoint
    """
    auth.login()

    json = [1, 2, 3]

    response = client.post(url + "/1/options", json=json)

    assert response.status_code == 200

    with app.app_context():
        question = Question.query.first()
        options_array = question.options.all()

        for index, option in enumerate(options_array):
            assert option.id == json[index]


def test_add_options_to_question_failure(app, client, auth, questions,
                                         options):
    """
    Tests add_options endpoint failure cases
    """
    auth.login()

    json = {"option_id": 1}
    response = client.post(url + "/1/options", json=json)
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    json = []
    response = client.post(url + "/1/options", json=json)
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    json = [1, 2, 3]

    response = client.post(url + "/999/options", json=json)
    assert response.status_code == 404

    json = [1, "ert", 3]

    response = client.post(url + "/1/options", json=json)
    assert response.status_code == 400
    assert response.get_json()["message"] == "option id must be an integer"

    with app.app_context():
        question = Question.query.first()

        assert question.options.count() == 0


def test_delete_options_from_question_success(app, client, auth, questions,
                                              options):
    """
    Tests delete_options success cases
    """
    auth.login()

    with app.app_context():
        question = Question.query.first()
        options_array = Option.query.limit(5)

        for option in options_array:
            question.add_option(option)

        db.session.commit()

        assert question.options.count() == 5

    json = [1, 3, 5]

    response = client.delete(url + "/1/options", json=json)

    assert response.status_code == 200

    with app.app_context():
        question = Question.query.first()

        assert question.options.count() == 2

        for index in range(1, 6):
            if index in [2, 4]:
                assert question.has_option(index)
            else:
                assert not question.has_option(index)


def test_delete_options_from_question_failure(app, client, auth, questions,
                                              scholarships, options):
    """
    Tests delete_options failure cases
    """
    auth.login()

    with app.app_context():
        question = Question.query.first()
        options_array = Option.query.limit(5)

        for option in options_array:
            question.add_option(option)

        db.session.commit()

        assert question.options.count() == 5

    json = {"option_id": 1}
    response = client.delete(url + "/1/options", json=json)
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    json = []
    response = client.delete(url + "/1/options", json=json)
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    json = [2, 3]

    response = client.delete(url + "/9999/options", json=json)
    assert response.status_code == 404

    json = ["asdf", 3]
    response = client.delete(url + "/1/options", json=json)
    assert response.status_code == 400
    assert response.get_json()["message"] == "option id must be an integer"

    with app.app_context():
        question = Question.query.first()

        assert question.options.count() == 5