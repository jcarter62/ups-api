from db import SystemsDB
from .site import Site

class Sites:

    def __init__(self):
        self.sites = []
        self.load_sites()


    def load_sites(self):
        db = SystemsDB()
        sites = db.query_all_records()
        for site in sites:
            self.sites.append(Site(site[0], site[1], site[2], site[3]))

