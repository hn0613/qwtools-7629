#coding:utf-8
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def generate_id(model_class, prefix=''):
    """
    生成基于日期的 ID 字符串。

    替代 view_SRC、view_SubDomain、Webinfo_add 中重复的 ID 生成逻辑：
        try: num = Model.objects.latest('id').id / except: num = 0
        id = prefix + date + str(num)

    Args:
        model_class: Django 模型类，用于查询最新 ID。
        prefix: ID 前缀（子域名用 'sd'，其余为空）。

    Returns:
        形如 '202606140' 或 'sd202606140' 的字符串。
    """
    try:
        num = model_class.objects.latest('id').id
    except model_class.DoesNotExist:
        num = 0
    return prefix + time.strftime('%Y%m%d', time.localtime(time.time())) + str(num)


def paginate(queryset, page_number, per_page=7):
    """
    对 QuerySet 分页，自动处理非法页码。

    替代 view_SRC、view_SubDomain 中重复的 Paginator + try/except 逻辑。

    Args:
        queryset: 待分页的 QuerySet。
        page_number: 来自 request.GET 的页码参数。
        per_page: 每页条数（默认 7，与原有一致）。

    Returns:
        Page 对象（始终有效，无效页码自动回退到首页或末页）。
    """
    paginator = Paginator(queryset, per_page)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page
