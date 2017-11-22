from app import db
from models_technologies import technologies


def import_technologies():
    with open("technology.txt", "r+") as file:
        for line in file:
            tech_obj = technologies(line)
            print (tech_obj.name)
            db.session.add(tech_obj)

def show_technologies():
    all_tech = db.session.query(technologies).all()
    output = ""
    for tech in all_tech:
        print (tech.name)
        output = output + tech.name + "\n"
    return output
    