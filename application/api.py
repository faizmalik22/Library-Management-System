from flask_restful import Api, Resource, reqparse
from .models import *
from flask_restful import fields, marshal_with

api = Api()


resource_fields = {
    'id':   fields.Integer,
    'name': fields.String,
    'description':  fields.String,
    'date_created': fields.DateTime
}

create_section_parser = reqparse.RequestParser()
create_section_parser.add_argument('name')
create_section_parser.add_argument('description')
create_section_parser.add_argument('date_created')
create_section_parser.add_argument('search')


update_section_parser = reqparse.RequestParser()
update_section_parser.add_argument('name')
update_section_parser.add_argument('description')
update_section_parser.add_argument('search')




class Section(Resource):
    @marshal_with(resource_fields)
    def get(self, user_id):  
        this_user = Users.query.get(user_id)
        if this_user and this_user.id == 1:
            sections = Sections.query.all()
            return sections
        else:
            return "", 404

    def post(self, user_id):
        this_user = Users.query.get(user_id)
        if this_user and this_user.id == 1:
            received_data = create_section_parser.parse_args()
            create_time = datetime.now()
            search = search_string_convert(received_data["name"])
            new_section = Sections(name=received_data["name"], description=received_data["description"], date_created=create_time, search=search)
            db.session.add(new_section)
            db.session.commit()
            return "Section Created Successfully" , 201
        else:
            return "", 404
        
    def put(self, user_id, section_id):
        this_user = Users.query.get(user_id)
        if this_user and this_user.id == 1:
            received_data = update_section_parser.parse_args()
            section = Sections.query.get(section_id)

            section.name = received_data["name"]
            section.description = received_data["description"]
            section.search = search_string_convert(received_data["name"])

            db.session.commit()
            return "Section Updated Successfully" , 201
        else:
            return "", 404
    def delete(self, user_id, section_id):
        this_user = Users.query.get(user_id)
        if this_user and this_user.id == 1:
            section = Sections.query.get(section_id)
            sections_books_association = SectionsBooks.query.filter_by(section_id=section_id).all()
            
            db.session.delete(section)
            for i in sections_books_association:
                db.session.delete(i)

            db.session.commit()
            return "Section Deleted Successfully" , 201
        else:
            return "", 404


api.add_resource(Section, '/api/section/<int:user_id>', '/api/section/<int:user_id>/<int:section_id>')










def search_string_convert(a):
  b = a.split()
  c = ""
  for i in b:
    c = c + i.lower()
  return c