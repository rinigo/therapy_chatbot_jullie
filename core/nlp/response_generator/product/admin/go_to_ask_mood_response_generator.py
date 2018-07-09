import models
from common.constant.user_status import UserStatus
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class GoToAskMoodResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            self.user.update_status(UserStatus.REGULAR.value)

            exists_session = len(models.Session.find_latest_session_data(self.user.id)) != 0

            if exists_session:
                models.Session.admin_update_status_asking_comment(self.user.id)
            else:
                models.Session.admin_create_asking_comment_session(self.user.id)

            print("\n[ADMIN] Ask mood")

            self.set_regular_response(['asked_commend'])

            return self.response_data
        except:
            return self.get_error_response_data()
