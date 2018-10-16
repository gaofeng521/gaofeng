from urllib import request

from django.core.cache import cache
from django.shortcuts import render

from . import models

def getAllArticle():
    """
    缓存查询的文章
    ：return:返回所有文章的一个列表
    """
    print("开始加载首页数据")

    articles=cache.get("alArtcle")
    if articles is None:
        print("数据库中没有数据， 开始查询数据。。。。")
        articles = models.Article.objects.all()
        print("数据中查询到数据库，同步到缓存中")
        cache.set("allAricle", articles)
    # return render(request,"blog/index.html",{"articles":articles})
    else:
        print("缓存中有数据...,不在查询数据库")