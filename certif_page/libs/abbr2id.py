#todo 将学校缩写转成学校id
from certif_page.libs.cache import cache

@cache.memoize(600)  # 缓存10分钟
def abbr2id(abbr)->int:
    id = 1
    return id