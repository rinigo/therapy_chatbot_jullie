import models
from common.constant.user_status import UserStatus
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class RestartSessionResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            self.user.update_status(UserStatus.REGULAR.value)

            models.Session.update_existing_sessions(self.user.id)

            models.Session.create_new_session(self.user.id)

            print("\n[ADMIN] Restarted session")

            self.set_regular_response(['restarted_session'])

            return self.response_data
        except:
            return self.get_error_response_data()
