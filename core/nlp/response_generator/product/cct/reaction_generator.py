import logging
import pandas as pd
from common.constant.df_from_csv import SP_I_DF, SP_O_DF, LISTENING_DF
from common.constant.message_type import MessageType
from random import shuffle
import models
import numpy as np


class ReactionGenerator:
    @classmethod
    def generate_reaction_by_type(cls, user_id, reaction_type, text_kw_df):
        try:
            used_reaction_numbers_list = models.Reaction.find_used_reaction_number(user_id, reaction_type)

            if reaction_type == MessageType.SPECIAL.value:
                responses = [
                    cls.__find_special_reaction(used_reaction_numbers_list, text_kw_df, user_id, reaction_type)
                ]
            else:
                responses = [
                    cls.__find_basic_reaction(used_reaction_numbers_list, user_id, reaction_type)]

            return responses
        except:
            logging.exception('')
            return []

    @staticmethod
    def generate_listening():
        try:
            listening = LISTENING_DF[LISTENING_DF.type == 1].text.values
            response_list = [np.random.choice(listening, 1)[0]]
            return response_list
        except:
            logging.exception('')
            return []

    @classmethod
    def __find_special_reaction(cls, used_reaction_numbers_list, text_kw_df, user_id, reaction_type):
        special_words = text_kw_df[text_kw_df.special != 'normal'].word.tolist()
        special_word = special_words[-1]

        # e.g. id = alone, cry, etc
        special_word_id = SP_I_DF[SP_I_DF.word == special_word]['id'].values[0]
        target_id_list = SP_O_DF[SP_O_DF['id'] == special_word_id].index.tolist()

        if len(used_reaction_numbers_list) == len(target_id_list):
            models.Reaction.enable_reaction_number(user_id, reaction_type)
            sp_id_list = used_reaction_numbers_list
        else:
            sp_id_list = SP_O_DF[
                (SP_O_DF.id == special_word_id)
                & ~(SP_O_DF.index.isin(used_reaction_numbers_list))
                ].index.tolist()

        shuffle(sp_id_list)
        sp_id = sp_id_list[0]

        models.Reaction.disable_reaction_number(user_id, sp_id, reaction_type)
        sp_reaction = SP_O_DF[SP_O_DF.index == sp_id].output.values[0]

        sp_reaction = sp_reaction.replace('\\n', '\n')

        return sp_reaction

    @classmethod
    def __find_basic_reaction(cls, used_reaction_numbers_list, user_id, reaction_type):
        try:
            used_reaction_numbers_list = list(set(used_reaction_numbers_list))

            rdf = pd.read_csv('./csv_files/reactions.csv')

            target_id_list = rdf[rdf['type'] == reaction_type].index.tolist()

            if any(i not in target_id_list for i in used_reaction_numbers_list):
                # In this case, reactions.csv has changed. so set all reations status = 1
                models.Reaction.enable_reaction_number(user_id, None, used_reaction_numbers_list)
                candidate_id_list = target_id_list

            elif len(used_reaction_numbers_list) == len(target_id_list):
                models.Reaction.enable_reaction_number(user_id, reaction_type)
                candidate_id_list = used_reaction_numbers_list

            else:
                candidate_id_list = rdf[
                    (rdf['type'] == reaction_type)
                    & ~(rdf.index.isin(used_reaction_numbers_list))
                    ].index.tolist()

            shuffle(candidate_id_list)
            r_id = candidate_id_list[0]

            models.Reaction.disable_reaction_number(user_id, r_id, reaction_type)

            r = rdf[rdf.index == r_id].reaction.values[0]
            r = r.replace('\\n', '\n')

            return r
        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return ''
