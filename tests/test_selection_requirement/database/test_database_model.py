import app as application
from app.models import option as option_model
from app.models import question as question_model
from app.models import association_tables
from app.models import scholarship as scholarship_model


def test_selection_requirement(app, scholarships, questions, options):
    """
    Test selection requirement
    """

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        options_array = option_model.Option.query.limit(5).all()
        questions_array = question_model.Question.query.limit(5).all()

        for question in questions_array:
            scholarship.add_selection_requirement(question)

        assert scholarship.selection_requirements.count() == 5

        selection_requirement = scholarship.selection_requirements.filter(
            association_tables.SelectionRequirement.question_id ==
            questions_array[2].id).first()
        scholarship.remove_selection_requirement(selection_requirement)

        selection_requirement = scholarship.selection_requirements.filter(
            association_tables.SelectionRequirement.question_id ==
            questions_array[4].id).first()
        scholarship.remove_selection_requirement(selection_requirement)

        assert scholarship.selection_requirements.count() == 3

        for id, question in enumerate(questions_array):
            if (id == 2 or id == 4):
                assert not scholarship.has_selection_requirement(question.id)
            else:
                assert scholarship.has_selection_requirement(question.id)

        selection_requirement = scholarship.selection_requirements.first()

        for option in options_array:
            selection_requirement.add_option(option)

        assert selection_requirement.options.count() == 5

        selection_requirement.remove_option(options_array[2])
        selection_requirement.remove_option(options_array[4])

        assert selection_requirement.options.count() == 3

        for id, option in enumerate(options_array):
            if (id == 2 or id == 4):
                assert not selection_requirement.has_option(option.id)
            else:
                assert selection_requirement.has_option(option.id)