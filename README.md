# 校园认证爬虫
## 有什么用？
1. 用于支持验证本科生、研究生、~~教职工~~的在校身份。
2. 获取其姓名、帐号、专业、年级、班级、性别和学籍照片等，实际上想获取教务系统上的啥就加几个正则表达式就行。
3. 收集用户输入正确的验证码图片。   

（目前仅支持陕西师范大学，欢迎其他学校的宝宝提交代码）

## 如何使用
1. 修改   
* */certif_page/config/setting.py* 里的 *IMG_NET_PREFIX* 这是指向本服务器的**网址**。

* */certif_page/api/学校名缩写* 即对应学校的api视图函数所在 *certif.py* 文件中写认证相关函数。

* */certif_page/api/学校名缩写/URL.py* 存储认证相关的网址，具体见注释说明。

* */certif_page/api/学校名缩写/IDENTITY.py* 存储前端传来的身份代码与其代表的身份信息的映射。

2. 添加
* 在 */certif_page/config/* 下添加[flask配置文件](http://www.pythondoc.com/flask/config.html "配置处理")
3. "*/static + /学校英文缩写/*" 存储验证码图片的本地路径，可通过公网访问。
4. "*/static + /学校英文缩写/portrait/*" 存储认证后获得的用户头像，**不可**通过公网访问。
5. */certif_page/models* 里存放着模型（数据库表）,用来存储获取的cookie。


## 没技术的细节
1. 使用了flask框架+mysql,redis数据库。
2. 使用request库，带着cookie去认证就好。
3. 对flask_sqlalchemy做了简单包装，实现auto_commit()功能，同时本身是线程安全的。

## 项目功能流程图
![功能流程图](certifBlueprint.png)

## TODO
- [x] json + redis使认证过程更快且数据结构更灵活。
- [x] 建立 apiKey 数据库，调用需要给出apiKey。
- [x] 为不同apiKey设置权限，同时允许公网访问用户头像。
- [ ] 建立代理服务器数据库，搭建内网穿透的服务器，应对校园网禁止公网访问的情况。
- [x] 规范项目目录名称。
- [ ] 利用获取的用户头像等信息，用face_recognition库实现学生证信息自动审核功能。
- [ ] 使用学生信息 + 黄牛邀请机制，实现分析用户间关系图谱的功能，进而实现周边广告精准投放功能（V3.0）。