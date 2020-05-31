from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse
import common
from common import ret_api, ret_api_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wanted.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Api
class Search(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('lang', type=str)
        parser.add_argument('search_type', type=str)
        parser.add_argument('keyword', type=str)
        parser.add_argument('max_cnt', type=int)
        args = parser.parse_args()

        search_type = args['search_type'] or None
        lang = args['lang'] or None
        max_cnt = args['max_cnt'] or 1

        if max_cnt <= 0:
            return ret_api(common.REQ_COUNT_ERROR)

        if not lang:
            return ret_api(common.NO_LANGUAGE)
        elif lang not in common.LANG_LIST:
            return ret_api(common.NO_SUPPORT_LANGUAGE)

        if search_type == 'name':
            name = args['keyword'] or ''
            max_cnt = args['max_cnt'] or 1

            if len(name) <= 0:
                if lang == common.LANG_KOR:
                    result_list = db.session.query(Company).filter(Company.name_ko != "").all()
                elif lang == common.LANG_JPN:
                    result_list = db.session.query(Company).filter(Company.name_jp != "").all()
                elif lang == common.LANG_ENG:
                    result_list = db.session.query(Company).filter(Company.name_en != "").all()

            else:
                if lang == common.LANG_KOR:
                    search = Company.name_ko.like(f'%{name}%')
                    result_list = db.session.query(Company).filter(search).all()
                elif lang == common.LANG_JPN:
                    search = Company.name_jp.like(f'%{name}%')
                    result_list = db.session.query(Company).filter(search).all()
                elif lang == common.LANG_ENG:
                    search = Company.name_en.like(f'%{name}%')
                    result_list = db.session.query(Company).filter(search).all()

            if len(result_list) > max_cnt:
                result_list = result_list[:max_cnt]

            data = []
            for result in result_list:
                data.append(result.get_company_info(lang))

            return ret_api_data(common.OK, data)
        elif search_type == 'tag':
            tag = args['keyword'] or None

            if lang == common.LANG_KOR:
                result_list = db.session.query(Company).filter(Company.tag_ko != "").all()
            elif lang == common.LANG_JPN:
                result_list = db.session.query(Company).filter(Company.tag_jp != "").all()
            elif lang == common.LANG_ENG:
                result_list = db.session.query(Company).filter(Company.tag_en != "").all()

            data = []
            for result in result_list:
                if tag in result.get_company_tag(lang):
                    data.append(result.get_company_info(lang))

            if len(data) > max_cnt:
                data = data[:max_cnt]

            return ret_api_data(common.OK, data)
        else:
            return ret_api(common.BAD_INPUT)


class Tag(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str)
        parser.add_argument('tag_ko', type=str)
        parser.add_argument('tag_jp', type=str)
        parser.add_argument('tag_en', type=str)
        args = parser.parse_args()
        type = args['type'] or None

        if type == 'add':
            tag_ko = args['tag_ko'] or None
            tag_jp = args['tag_jp'] or None
            tag_en = args['tag_en'] or None
            if tag_ko is None or tag_jp is None or tag_en is None:
                return ret_api(common.BAD_INPUT)

            tag = Tag(tag_ko=tag_ko, tag_en=tag_en, tag_jp=tag_jp)
            db.session.add(tag)
            db.session.commit()
            ret_api(common.OK)

        else:
            return ret_api(common.BAD_INPUT)


class CompanyTag(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('lang', type=str)
        parser.add_argument('id', type=str)
        parser.add_argument('type', type=str)
        parser.add_argument('tag', type=str)

        args = parser.parse_args()

        type = args['type'] or None
        id = args['id'] or None
        tag = args['tag'] or None
        lang = args['lang'] or None

        if not lang:
            return ret_api(common.NO_LANGUAGE)
        elif lang not in common.LANG_LIST:
            return ret_api(common.NO_SUPPORT_LANGUAGE)

        if tag is None or id is None:
            return ret_api(common.BAD_INPUT)

        tags = self.get_tags(lang, tag)
        if tags is None:
            return ret_api(common.NO_TAG)

        if type == 'add':
            company = db.session.query(Company).filter(Company.id == id).first()
            if company is None:
                return ret_api(common.NO_COMPANY)

            if len(company.tag_ko) > 0 :
                company.tag_ko += f"|{tags['tag_ko']}"
                company.tag_en += f"|{tags['tag_en']}"
                company.tag_jp += f"|{tags['tag_jp']}"
            else:
                company.tag_ko = tags['tag_ko']
                company.tag_en = tags['tag_en']
                company.tag_jp = tags['tag_jp']

            db.session.commit()
            return ret_api(common.OK)

        elif type == 'del':
            company = db.session.query(Company).filter(Company.id == id).first()
            if company is None:
                return ret_api(common.NO_COMPANY)
            try:
                tag_ko_list = company.tag_ko.split('|')
                tag_ko_list.remove(tags['tag_ko'])
                company.tag_ko = '|'.join(tag_ko_list)
                tag_en_list = company.tag_en.split('|')
                tag_en_list.remove(tags['tag_en'])
                company.tag_en = '|'.join(tag_en_list)
                tag_jp_list = company.tag_jp.split('|')
                tag_jp_list.remove(tags['tag_jp'])
                company.tag_jp = '|'.join(tag_jp_list)

            except:
                return ret_api(common.DATA_ERROR)

            db.session.commit()
            return ret_api(common.OK)

        else:
            return ret_api(common.REQ_COUNT_ERROR)

    def get_tags(self, lang, tag):
        if lang == common.LANG_KOR:
            data = db.session.query(Tag).filter(Tag.tag_ko == tag).first()
        elif lang == common.LANG_JPN:
            data = db.session.query(Tag).filter(Tag.tag_jp == tag).first()
        elif lang == common.LANG_ENG:
            data = db.session.query(Tag).filter(Tag.tag_en == tag).first()
        else:
            return None

        if data:
            return data.get_tags()
        else:
            return None


# Url
api = Api(app)
api.add_resource(Search, '/search')
api.add_resource(Tag, '/tag')
api.add_resource(CompanyTag, '/company_tag')


# Models
class Company(db.Model):
    __table_name__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name_ko = db.Column(db.String(100), nullable=True)
    name_jp = db.Column(db.String(100), nullable=True)
    name_en = db.Column(db.String(100), nullable=True)
    tag_ko = db.Column(db.String(255), nullable=True)
    tag_en = db.Column(db.String(255), nullable=True)
    tag_jp = db.Column(db.String(255), nullable=True)

    def get_dict(self):
        return dict(id=self.id,
                    name_ko=self.name_ko,
                    name_jp=self.name_jp,
                    name_en=self.name_en,
                    tag_ko=self.tag_ko,
                    tag_jp=self.tag_jp,
                    tag_en=self.tag_en,
                    )

    def get_company_info(self, lang):
        if lang == "ko":
            if len(self.name_ko) > 0:
                name = self.name_ko
            elif len(self.name_en) > 0:
                name = self.name_en
            else:
                name = self.name_jp
            return dict(id=self.id, name=name, tag=self.tag_ko.split("|"))
        elif lang == "jp":
            if len(self.name_jp) > 0:
                name = self.name_jp
            elif len(self.name_en) > 0:
                name = self.name_en
            else:
                name = self.name_ko
            return dict(id=self.id, name=name, tag=self.tag_jp.split("|"))
        elif lang == "en":
            if len(self.name_en) > 0:
                name = self.name_en
            elif len(self.name_ko) > 0:
                name = self.name_ko
            else:
                name = self.name_jp
            return dict(id=self.id, name=name, tag=self.tag_en.split("|"))

    def get_company_tag(self, lang):
        if lang == "ko":
            return self.tag_ko.split("|")
        elif lang == "jp":
            return self.tag_jp.split("|")
        elif lang == "en":
            return self.tag_en.split("|")


class Tag(db.Model):
    __table_name__ = 'tag'

    tag_id = db.Column(db.Integer, primary_key=True)
    tag_ko = db.Column(db.String(100), unique=True, nullable=False)
    tag_en = db.Column(db.String(100), unique=True, nullable=False)
    tag_jp = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, tag_ko, tag_en, tag_jp):
        self.tag_ko = tag_ko
        self.tag_en = tag_en
        self.tag_jp = tag_jp

    def get_tags(self):
        return dict(tag_ko=self.tag_ko, tag_en=self.tag_en, tag_jp=self.tag_jp)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
