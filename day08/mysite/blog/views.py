from io import BytesIO
import uuid

import cacheutils as cacheUtils
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, reverse
# from django.core.urlresolvers import reverse
from django.core.cache import cache

from . import models
from . import utils
from . import cacheUtils


def articles(args):
    pass


def index(request):
    article=models.Article.objects.all()
    return render(request, "blog/index.html", {"articles": article})


def add_user(request):
    return render(request, "blog/add_user.html", {})


def delete_user(request, user_id):
    user = models.User.objects.get(pk=user_id)
    user.delete()
    return redirect(reverse("blog:list_user"))


def list_user(request):
    users = models.User.objects.all()
    return render(request, "blog/user_list.html", {"users": users})


def reg(request):
    if request.method == "GET":
        return render(request, "blog/add_user.html", {"msg": "请认真填写如下选项"})
    elif request.method == "POST":
        # 接受参数
        try:
            username = request.POST["username"].strip()
            password = request.POST.get("password").strip()  # .getlist()
            confirmpwd = request.POST.get("confirmpwd").strip()
            nickname = request.POST.get("nickname", None)
            avatar = request.FILES.get("avatar", 'static/img/default.png')

            # code = request.POST['code']
            #
            # mycode = request.session["code"]
            # if code.upper() != mycode.upper():
            #     return render(request, "blog/add_user.html", {"msg": "验证码错误，请重新输入！！"})
            #
            # # 删除session中验证码
            # del request.session["cdoe"]

            # 数据校验
            if len(username) < 1:
                return render(request, "blog/add_user.html", {"msg": "用户名称不能为空！！"})
            if len(password) < 6:
                return render(request, "blog/add_user.html", {"msg": "密码长度不能小于6位！！"})
            if password != confirmpwd:
                return render(request, "blog/add_user.html", {"msg": "两次密码不一致！！"})
            # 用户名称是否重复
            try:
                user = models.User.objects.get(name=username)
                return render(request, "blog/add_user.html", {"msg": "该用户名称已经存在，请重新填写！！"})
            except:
                # 先对密码加密，之后在保存
                password = utils.hmac_by_md5(password)

                user = models.User(name=username, password=password, nickname=nickname, header=avatar)
                user.save()
                return render(request, "blog/login.html", {"msg": "恭喜您，注册成功！！"})
        except:
            return render(request, "blog/add_user.html", {"msg": "对不起，用户名称不能为空！！"})


def show(request, u_id):
    user = models.User.objects.get(pk=u_id)
    return render(request, "blog/show.html", {"user": user})


def update(request, u_id):
    if request.method == "GET":
        user = models.User.objects.filter(id=u_id).first()
        return render(request, "blog/update.html", {"user": user})
    else:
        nickname = request.POST["nickname"]
        age = request.POST['age']

        # 数据校验

        # 如何修改？？？？？？？？？？
        # 第一步，获取用户
        user = models.User.objects.get(pk=u_id)
        # 第二步，修改值
        user.age = age
        user.nickname = nickname
        # 第三步， 保存
        user.save()

        return redirect(reverse("blog:show", args=(u_id,)))


def login(request):
    """
    登录的视图函数，完成用户登录功能
    :param request: 请求头对象
    :return:
    """
    if request.method == "GET":
        return render(request, "blog/login.html", {"msg": "请登录"})
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # TODO 将来需要完善验证码
        # code = request.POST["code"]

        try:
            password = utils.hmac_by_md5(password)
            user = models.User.objects.get(name=username, password=password)
            # 使用session来记录登录用户的信息
            request.session["loginUser"] = user
            # 使用cookie记住用户名称
            response = redirect(reverse("blog:index"))
            # cookie不能存储中文
            response.set_cookie("username", user.name, max_age=3600 * 24 * 14)
            return response
        except:
            return  render(request, "blog/login.html", {"msg": "登录失败，请重新登录！！"})


def logout(req):
    try:
        del req.session["loginUser"]
    finally:
        return redirect(reverse("blog:index"))


def add_article(request):
    if request.method == "GET":
        return render(request, "blog/add_article.html", {"msg": "请开始创作"})
    else:
        title = request.POST["title"]
        content = request.POST["content"]
        author = request.session["loginUser"]

        # 验证
        article = models.Article(title=title, content=content, author=author)
        article.save()
        return render(request,'blog/index.html',{'msg':'发表完成'})

        #将缓存重新更新
        # cacheUtils.getAllArticle(ischanage=True)
        # return redirect(reverse("blog:show_arcticle", kwargs={"a_id": article.id }))


def delete_article(request, a_id):
    at = models.Article.objects.get(pk=a_id)
    at.delete()
    return redirect(reverse("blog:index"))


def update_article(request, a_id):
    at = models.Article.objects.get(pk=a_id)
    if request.method == "GET":
        return render(request, "blog/update.html", {"article": at})
    else:
        title = request.POST["title"]
        content = request.POST["content"]
        at.title = title
        at.content = content
        at.save()
        return redirect(reverse("blog:show_arcticle", kwargs={"a_id": a_id}))


def show_article(request):
    """
    :param request:
    :param a_id:
    :return:
    """
    at = models.Article.objects.all()
    return render(request, "blog/show_article.html", {"article": at})



def code(request):
    img, code = utils.create_code()
    # 首先需要将code保存到session中
    request.session['code'] = code
    # 返回图片
    file = BytesIO()
    img.save(file, 'PNG')

    return HttpResponse(file.getvalue(), "image/png")


#注销

def esc_user(request):
    try:
        del request.session['loginUser']
        return render(request,'blog/login.html/',{"msg":'已注销，请重新登录！！'})
    except:
        return  render(request,'blog/index.html/',{"msg":'网络断了，退出失败！'})

def del_article(request):
   art_id = request.GET["id"]
   article=models.Article.objects.get(pk=art_id)
   article.delete()
   return render(request, "blog/show_article.html/", {"msg": "已删除成功！！"})


#修改文章
def update_article(request,a_id):
    articles = models.Article.objects.get(id=a_id)
    if request.method == 'GET':
       return render(request, 'blog/update_article.html', {'article': articles})
    else:
        title = request.POST["title"]
        content = request.POST['content']
        print(title,content)
        articles.title=title
        articles.content=content
        articles.save()
        return redirect(reverse("blog:show_article"),{"msg":"文章修改成功！！"})