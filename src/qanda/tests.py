from django.test import TestCase
from unittest.mock import patch
from django.conf import settings
from django.contrib.auth import get_user_model
from elasticsearch import Elasticsearch
from .models import Question


class QuestionSaveTestCase(TestCase):
    """
    A test for Question.save()
    """

    @patch('qanda.service.elasticsearch.Elasticsearch')
    def test_elasticsearch_upsert_on_save(self, ElasticsearchMock):
        user = get_user_model().objects.create_user(
            username='unittest',
            password='unittest',
        )
        question_title = 'Unit test'
        question_body = 'Body of unittest'
        q = Question(
            title=question_title,
            question=question_body,
            user=user,
        )
        q.save()

        self.assertIsNotNone(q.id)
        self.assertTrue(ElasticsearchMock.called)
        mock_client = ElasticsearchMock.return_value
        mock_client.update.assert_called_once_with(
            settings.ES_INDEX,
            id=q.id,
            body={
                'doc': {
                    '_type': 'doc',
                    'text': '{}\n{}'.format(question_title, question_body),
                    'question_body': question_body,
                    'title': question_title,
                    'id': id,
                    'created': q.created,
                },
                'doc_as_upsert': True,
            }
        )
