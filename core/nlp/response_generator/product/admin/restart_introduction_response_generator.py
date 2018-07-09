from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
from scripts.delete_user_from_db import delete_all_rows_of_a_user


class RestartIntroductionResposneGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            delete_all_rows_of_a_user(self.user.id, from_messenger=True)

            return self.response_data
        except:
            return self.get_error_response_data()
