from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
import numpy as np


class AboutBreakupResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            response = self.__create_response_about_breakup()

            self.set_regular_response(response)

            return self.response_data
        except:
            return self.get_error_response_data()

    @classmethod
    def __create_response_about_breakup(cls):
        qr = [
            ["I’m sorry to hear that"],
            ["it is sad to hear that"],
            ["omg.."],
        ]

        cmp_list = [
            ["it is always just so tough..since you shared your lives together for however long you were together😔"],
            ["i know its rough time that you miss the good memories you had with your ex right😞"],
            ["it must be a hard time for you cuz love doesn't go away that easily right😢"],
        ]

        np.random.shuffle(qr)
        np.random.shuffle(cmp_list)

        return qr[0] + cmp_list[0]
