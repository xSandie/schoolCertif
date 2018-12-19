# -*- coding:utf-8 -*- 
from sqlalchemy import Column, Integer, String#数据类型从原来的sqlachemy导入
from certif_page.models.base import Base

class SnnuCookie(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId=Column(String(100),nullable=False)
    JSESSIONID=Column(String(100))
    csrf__EVENTVALIDATION=Column(String(500))
    csrf__VIEWSTATEGENERATOR=Column(String(100))
    csrf__VIEWSTATE=Column(String(300))
    imgUrl=Column(String(150))

