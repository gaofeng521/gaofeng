from django.contrib import admin

# Register your models here.
from . import models


class UserAdmin(admin.ModelAdmin):
    #列表时显示的类型
    list_display = ["name","nickname","age","birthday"]
    #列表时过滤字段
    list_filter = ("name","age","nickname")
    #进行分页，每页两条数据
    list_per_page = 2

    #list_editable=["nickname","age"]
    list_display_links = ["age","nickname"]

    #显示风格
    #fields=["name","nickname",""age]

    #显示风格2，与上面不能同时出现

    fieldsets = [
        ("base",{"fields":["age","birthday"]}),
        ("other",{"fields":["name","nickname"]}),
    ]



admin.site.register(models.User)
admin.site.register(models.Article)