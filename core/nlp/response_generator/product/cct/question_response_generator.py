import logging
import numpy as np
import models
from common.constant.intent_type import Intent
from common.constant.message_type import MessageType
from common.constant.string_constant import StringConstant
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
from core.nlp.question import question
from core.nlp.response_generator.product.cct.reaction_generator import ReactionGenerator


class QuestionResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            responses = []

            session_started_time = models.Session.fetch_session_started_time(self.user.id)
            session_ended_time = models.Session.fetch_session_ended_time(self.user.id)

            past_response_types = models.Response.fetch_all_response_type_during(session_started_time,
                                                                                 session_ended_time,
                                                                                 self.user.id)

            # still get duplicated types since all response_generator in same cluster_id have same types.
            # so damp the types of cluster_id we already checked
            response_type_list = []
            checked_cluster_ids = []
            for response_type in past_response_types:
                if response_type[0] in checked_cluster_ids:
                    pass
                else:
                    checked_cluster_ids.append(response_type[0])
                    response_type_list += response_type[1].split()

            number_of_question_so_far = response_type_list.count(MessageType.QUESTION.value)
            question_sidx = [idx for idx, intent in enumerate(self.message.intent_list) if
                             intent.value in Intent.PROPER_QUESTION_TYPES.value]

            if number_of_question_so_far == 0:
                responses += np.random.choice(StringConstant.asked_advise_list.value, 1)[0]

            elif number_of_question_so_far < 3:
                question_type = question.DefineQuestionType(self.message.text_df[self.message.text_df.sidx.isin(question_sidx)]).categorize_by_leading_word()
                if question_type.class_name in {"UnknownQuestionType", "AgreeQuestionType"}:
                    responses += ReactionGenerator.generate_listening()
                else:
                    responses += question_type.answer

            else:
                question_type = question.DefineQuestionType(self.message.text_df[self.message.text_df.sidx.isin(question_sidx)]).categorize_by_leading_word()
                if question_type.class_name in {"UnknownQuestionType", "AgreeQuestionType"}:

                    responses += ReactionGenerator.generate_listening()
                else:
                    responses += question_type.answer

            self.response_data['regular'] = responses

            return self.response_data
        except:
            logging.exception('')

            responses = ReactionGenerator.generate_listening()
            self.response_data['regular'] = responses

            return self.response_data
