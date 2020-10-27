import os
from flask import Flask, request, abort, jsonify,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    #   '''
    #   @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    #   '''

    CORS(app)

    #   '''
    #   @TODO: Use the after_request decorator to set Access-Control-Allow
    #   '''
    @app.after_request
    def after_request(response):
       response.headers.add('Access-Control-Allow-Headers',
                            'Content-Type,Authorization')
       response.headers.add('Access-Control-Allow-Method',
                            'GET,DELETE,POST,PATCH')
       return response

    # for formating question..
    def format_questions(questions):
            questions_list = []
            for question in questions:
                questions_list.append({
                    "question": question.question,
                    "answer": question.answer, 
                    "category": question.category, 
                    "difficulty": question.difficulty, 
                    "id": question.id 
                })
            return questions_list

    #   '''
    #   @TODO:
    #   Create an endpoint to handle GET requests
    #   for all available categories.
    #   '''


    @app.route('/categories')
    def get_Categories():
        category = Category.query.all()
        format_category={cat.id:cat.type for cat in category}
        response=jsonify({
            'success': True,
            'categories': format_category,
        })
        return response
    
    # for pagintion
    def paginate_Questions(request, selection):
        page_number = request.args.get('page', 1, type=int)
        start = (page_number - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = format_questions(selection)
        current_questions = questions[start:end]
        return current_questions
    
    # for ordering the question by id .
    def question_order():
        return Question.query.order_by(Question.id).all()

    #   ''' 
    #   @TODO:
    #   Create an endpoint to handle GET requests for questions,
    #   including pagination (every 10 questions).
    #   This endpoint should return a list of questions,
    #   number of total questions, current category, categories.

    #   TEST: At this point, when you start the application
    #   you should see questions and categories generated,
    #   ten questions per page and pagination at the bottom of the screen for three pages.
    #   Clicking on the page numbers should update the questions.
    #   '''
    @app.route('/questions')
    def get_questions():
        questions = question_order()
        if len(questions) == 0:
            abort(404)
        else:
            categories = Category.query.all()
            current_questions = paginate_Questions(request, questions)
            format_category={cat.id : cat.type for cat in categories}
            return jsonify({
                'success': True,
                'questions': current_questions,
                'totalQuestions':len(questions),
                'categories':format_category,
                'currentCategory': None
            })


    #   '''
    #   @TODO:
    #   Create an endpoint to DELETE question using a question ID.

    #   TEST: When you click the trash icon next to a question, the question will be removed.
    #   This removal will persist in the database and when you refresh the page.
    #   '''


    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question == None:
            abort(404)
        else:
            question.delete()
            questions=Question.query.all()
            categories=Category.query.all()
            format_questions=[question.format() for question in questions]
            format_categories=[Category.format() for Category in categories]
            return jsonify({
               'success': True,
               'questions': format_questions,
               'totalQuestions': len(questions),
               'categories': format_categories,
               'currentCategory': None
            })

    #   '''
    #   @TODO:
    #   Create an endpoint to POST a new question,
    #   which will require the question and answer text,
    #   category, and difficulty score.

    #   TEST: When you submit a question on the "Add" tab,
    #   the form will clear and the question will appear at the end of the last page
    #   of the questions list in the "List" tab.
    #   '''
    @app.route('/questions', methods=['POST'])
    def new_question():
        new_question=request.get_json()
        try:
            question = Question(question=new_question['question'], answer=new_question['answer'],
                                category=new_question['category'], difficulty=new_question['difficulty'])
            Question.insert(question)
            return jsonify({
                'success': True,
            })
        except:
             abort(422)


    #   '''
    #   @TODO:
    #   Create a POST endpoint to get questions based on a search term.
    #   It should return any questions for whom the search term
    #   is a substring of the question.

    #   TEST: Search by any
    # phrase. The questions list will update to include
    #   only question that include that string within their question.
    #   Try using the word "title" to start.
    #   '''
    
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        data = request.get_json()
        searchTerm = data.get('searchTerm', None)
        if (searchTerm is None):
            abort(404)
        else:
            Results = Question.query.filter(Question.question.ilike('%'+searchTerm+'%')).all()
            results_list = format_questions(Results)
            
            return jsonify({
                'success': True,
                'questions': results_list,
                'totalQuestions':len(Results),
                'currentCategory': None
            })


    #   '''
    #   @TODO:
    #   Create a GET endpoint to get questions based on category.

    #   TEST: In the "List" tab / main screen, clicking on one of the
    #   categories in the left column will cause only questions of that
    #   category to be shown.
    #   '''

    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        categrory = Category.query.filter_by(id=category_id).one()
        if (categrory is None):
            abort(404)
        questions = Question.query.filter_by(category=str(categrory.id)).all()
        format_questions = [ques.format() for ques in questions]
        if (questions is None):
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': format_questions,
                'totalQuestions': len(questions),
                'currentCategory':category_id
            })


    #   '''
    #   @TODO:
    #   Create a POST endpoint to get questions to play the quiz.
    #         This endpoint should take category and previous question parameters
    #      and return a random questions within the given category,
    #   if provided, and that is not one of the previous questions.

    #   TEST: In the "Play" tab, after a user selects "All" or a category,
    #   one question at a time is displayed, the user is allowed to answer
    #   and shown whether they were correct or not.
    #   '''

    ## get quizzes dose not work fix it ...
    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        data=request.get_json()
        if ('quiz_category' not in data and 'previous_questions' not in data):
             abort(400)
        try:
            category = data.get('quiz_category')
            previous_questions = data.get('previous_questions')
            category_id = category['id']

            if category_id == 0:
                list_questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
            else:
                list_questions = Question.query.filter_by(category=category_id).filter(Question.id.notin_((previous_questions))).all()
      
            
            question = list_questions[random.randrange(0, len(list_questions))].format()
            return jsonify({
                "success": True,
                "question": question
            })
      
        except:
            abort(422)
          

    #   '''
    #   @TODO:
    #   Create error handlers for all expected errors
    #   including 404 and 422.
    #   '''
    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
      }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
      return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
      }), 500

    @app.errorhandler(400)
    def bad_reqeust(error):
        return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Reqeust"
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
        }), 422



    return app
