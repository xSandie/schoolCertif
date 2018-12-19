# 校园认证爬虫
## 有什么用？
1. 用于支持验证本科生、研究生、~~教职工~~的在校身份。
2. 获取其姓名及帐号。
3. 收集用户输入正确的验证码图片。   

（目前仅支持陕西师范大学，欢迎其他学校的宝宝提交代码）

## 如何使用
1. 修改   
* */certif_page/libs/filehelper.py* 里的 *img_net_prefix* 这是指向服务器的**网址**。
* */certif_page/api/学校名缩写* 即对应学校的api视图函数所在 *certif.py* 文件中写认证相关函数。
* */certif_page/api/学校名缩写/url.py* 存储认证相关的网址，具体见注释说明。
2. 存储图片的本地路径为 "*/static + /学校英文缩写/*"
3. */certif_page/models* 里存放着模型（数据库表）,用来存储获取的cookie。


## 没技术的细节
1. 使用了flask框架+mysql数据库。
2. 使用request库，带着cookie去认证就好。
