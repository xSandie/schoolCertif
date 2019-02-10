# 校园认证爬虫
## 有什么用？
1. 用于支持验证本科生、研究生、~~教职工~~的在校身份。
2. 获取其姓名及帐号。
3. 收集用户输入正确的验证码图片。   

（目前仅支持陕西师范大学，欢迎其他学校的宝宝提交代码）

## 如何使用
1. 修改   
* */certif_page/libs/filehelper.py* 里的 *img_net_prefix* 这是指向本服务器的**网址**。

* */certif_page/api/学校名缩写* 即对应学校的api视图函数所在 *certif.py* 文件中写认证相关函数。

* */certif_page/api/学校名缩写/URL.py* 存储认证相关的网址，具体见注释说明。

* */certif_page/api/学校名缩写/IDENTITY.py* 存储前端传来的身份代码与其代表的身份信息的映射。

2. "*/static + /学校英文缩写/*" 存储验证码图片的本地路径，可通过公网访问。
3. "*/static + /学校英文缩写/portrait/*" 存储认证后获得的用户头像，**不可**通过公网访问。
4. */certif_page/models* 里存放着模型（数据库表）,用来存储获取的cookie。


## 没技术的细节
1. 使用了flask框架+mysql数据库。
2. 使用request库，带着cookie去认证就好。
3. 对flask_sqlalchemy做了简单包装，实现auto_commit()功能，同时本身是线程安全的。

## TODO
- [ ] json + redis使认证过程更快且数据结构更灵活。
- [ ] 建立 apiKey 数据库，调用需要给出apiKey
- [ ] 为不同apiKey 设置权限，同时允许公网访问用户头像
