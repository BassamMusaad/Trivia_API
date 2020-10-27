import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:123456789@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_Categories(self):
        response=self.client().get('/categories')
        self.assertEqual(response.status_code,200)
        data=json.loads(response.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
    
    def test_get_questions(self):
        response=self.client().get('/questions')
        self.assertEqual(response.status_code,200)
        data=json.loads(response.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['currentCategory'],None)


    def test_delete_question(self):
        response=self.client().delete('/questions/8')
        data=json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['currentCategory'],None)


    def test_new_question(self):
        response=self.client().post('/questions',json={
            "question":"Hi","category":1,"answer":"hi","difficulty":1})
        self.assertEqual(response.status_code,200)
        data=json.loads(response.data)
        self.assertEqual(data['success'],True)
        


    def test_search_question(self):
        response=self.client().post('/questions/search',json={
            "searchTerm":"what"
        })
        self.assertEqual(response.status_code,200)
        data=json.loads(response.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['currentCategory'],None)

    def test_get_category_questions(self):
        response=self.client().get('/categories/2/questions')
        self.assertEqual(response.status_code,200)
        data=json.loads(response.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['currentCategory'],2)


    def test_get_quizzes(self):
        response=self.client().post('/quizzes',json={'previous_questions': [],
                          'quiz_category': {'type': 'Entertainment', 'id': 5}})
        self.assertEqual(response.status_code,200)
        data=json.loads(response.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

    def test_400_if_the_any_error_in_get_quizzes(self):
        response=self.client().post('/quizzes',json={})
        self.assertEqual(response.status_code, 400)
        data=json.loads(response.data)
        
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad Reqeust')

    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()