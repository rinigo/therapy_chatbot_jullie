from scripts.delete_user_from_db import initialize_database


class DataAnalyzer(object):
    def __init__(self):
        self.session = initialize_database('production')

    def get_total_new_user_count(self, start_m, start_d, start_h, end_m, end_d, end_h):
       try:
           new_users = self.session.