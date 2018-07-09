from core.nlp.response_generator.factory.base_response_generator_factory import BaseResponseGeneratorFactory
from core.nlp.response_generator.product.intro.intro_response_generator import IntroResponseGenerator


class IntroResponseGeneratorFactory(BaseResponseGeneratorFactory):
    @classmethod
    def create(cls, user, message):
        return IntroResponseGenerator(user, message)
