from app import db
from app.models.question import Question

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
