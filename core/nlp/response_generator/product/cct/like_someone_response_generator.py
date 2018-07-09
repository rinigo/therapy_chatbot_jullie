from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
import numpy as np


class LikeSomeoneResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            response = self.__create_response_for_like_someone()

            self.set_regular_response(response)

            return self.response_data
        except:
            return self.get_error_response_data()

    @classmethod
    def __create_response_for_like_someone(cls):
        qr_list = [
            ["oh"],
            ["wow"],
        ]

        repeat_list = [
            ["thats sweet you like somebody😋"],
            ["so you are in love with the guy😜"],
            ["sounds you fell in love with the guy😍"],
        ]

        cmp_list = [
            ["i know love is not easy right"],
            ["sometimes love gives you happy and sometimes give you pain right"],
            ["its kinda hard to be lovers right"],
        ]
        np.random.shuffle(qr_list)
        np.random.shuffle(repeat_list)
        np.random.shuffle(cmp_list)

        return qr_list[0] + repeat_list[0] + cmp_list[0]
