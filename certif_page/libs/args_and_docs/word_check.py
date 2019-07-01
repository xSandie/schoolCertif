# 清洗参数，校验参数
import re


class WordCheck:
    address_regex = re.compile(r"[\u4e00-\u9fa5]+省|[\u4e00-\u9fa5]+市")
    fileMD5_regex = re.compile(r'^\b[A-F0-9]{32}\b$')
    uuid_regex = re.compile(r'^\w{3}_\w{12}$')
    check_number_regex = re.compile(r'^\d{6}$')
    birth_ym = re.compile(r'^\d{4}-\d{2}$')
    searchBar_regex = re.compile(r'[\'\"\*,;?=&\(\)\[\]\<\>%{}\\]|(update|delete|select)')
    username_regex = re.compile(r'[\*;?\\\+=&\(\)\[\]\<\>%{}]')
    email_regex = re.compile(r"\w[-\w.+&!#$%&'*+-/=?^_`{|}~]*@([A-Za-z0-9+-_]+\.)+[A-Za-z]{2,14}")
    url_regex = re.compile(r'(https?|ftp|file)://')
    tel_regex = re.compile(r'^1[0-9]{10}$')
    over_sea_tel_regex = re.compile(r'^[0-9\+\-\s]{11,15}$')
    digital_regex = re.compile(r'^-?\d+$')
    sso_suffix = re.compile(r'_(QQ|wb|wt)_\w{4}$')

    newline = re.compile(r'[\f\v]+|\r|</p>|</li>|</ul>|<br>|<br />', re.S)
    space = re.compile(r'<[^>]+>|\t', re.S)
    re_new_line = re.compile(r'\n{1,}', re.S)
    filepath_regex = re.compile(r'[A-F0-9][A-F0-9]/[A-F0-9][A-F0-9]/[A-F0-9]{32}.[A-Za-z]{1,10}', re.S)

    # 搜索参数格式
    searchArgs_regex = re.compile(r'[a-z]{1,2}-(?:\d+,\d+|[a-z]+|\d+)')
    pointUuid_regex = re.compile(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
    intern_date_regex = re.compile(r'\d{4}-\d{2}')
    split_regex = re.compile(r',|，|;|;| |、|。')

    @classmethod
    def get_search_args(cls, args_str):
        return cls.searchArgs_regex.findall(args_str)

    @classmethod
    def check_file_path(cls, text):
        rv = cls.filepath_regex.match(text)
        if not rv:
            return False
        return True

    @classmethod
    def split_str(cls, input_str):
        return re.split(cls.split_regex, str(input_str))

    @classmethod
    def get_intern_date(cls, args_str):
        return cls.intern_date_regex.findall(args_str)

    @classmethod
    def sso_name_format(cls, src_str):
        des_str = re.sub(cls.sso_suffix, '', src_str)
        return des_str

    @classmethod
    def check_file_md5(cls, text):
        rv = cls.fileMD5_regex.match(text)
        if not rv:
            return False
        return True

    @classmethod
    def check_filepath(cls, text):
        rv = cls.filepath_regex.match(text)
        if not rv:
            return False
        return True

    @classmethod
    def check_digital(cls, text):
        rv = cls.digital_regex.match(text)
        if not rv:
            return False
        return True

    @classmethod
    def get_address(cls, text):
        match = cls.address_regex.search(text)
        if match:
            result = match.group()
        else:
            result = u"其他地区"

        return result

    @classmethod
    def check_point_uuid(cls, text):
        match = cls.pointUuid_regex.match(str(text))
        if not match:
            return False
        return True

    @classmethod
    def check_uuid(cls, text):
        match = cls.uuid_regex.match(str(text))
        if not match:
            return False
        return True

    @classmethod
    def check_number(cls, text):
        match = cls.check_number_regex.match(str(text))
        if not match:
            return False
        return True

    @classmethod
    def check_birth_ym(cls, text):
        match = cls.birth_ym.match(str(text))
        if not match:
            return False
        return True

    @classmethod
    def check_search_bar(cls, text):
        """
        返回True表示正常，False表示有非法字符
        """
        if isinstance(text, str):
            match = cls.searchBar_regex.search(text)
            if not match:
                return True
            return False

        return True

    @classmethod
    def wash_sql_parmas(cls, parm):
        """
        清洗sql参数，如果有不合格的参数，直接清洗为''
        """
        if isinstance(parm, str):
            match = cls.searchBar_regex.search(parm)
            if not match:
                return parm
            return ''

        if isinstance(parm, dict):
            _dict = {}
            for (k, v) in parm.items():
                if isinstance(v, str):
                    match = cls.searchBar_regex.search(v)
                    if match:
                        _dict[k] = ''
                    else:
                        _dict[k] = v
                elif isinstance(v, int):
                    _dict[k] = v
                elif isinstance(v, list):
                    new_lst = []
                    for row in v:
                        match = cls.searchBar_regex.search(row)
                        if not match:
                            new_lst.append(row)
                    _dict[k] = new_lst
                else:
                    _dict[k] = ''

            return _dict

        if isinstance(parm, list):
            _list = []
            for v in parm:
                if isinstance(v, str):
                    match = cls.searchBar_regex.search(v)
                    if match:
                        _list.append('')
                    else:
                        _list.append(v)
                else:
                    _list.append('')

            return _list

        return parm

    @classmethod
    def wash_html(cls, html):
        return re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

    @classmethod
    def check_username(cls, text):
        """
        返回True表示正常，False表示有非法字符
        """
        if isinstance(text, str):
            match = cls.username_regex.search(text)
            if not match:
                return True
            return False

        return False

    @classmethod
    def check_email(cls, text):
        """
        返回True表示正常，False表示有非法字符
        """
        if isinstance(text, str):
            # print '--------------->', text
            match = cls.email_regex.match(text)
            if not match:
                return False
            return True

        return False

    @classmethod
    def wash_email(cls, text):
        """
        清洗Email ，错误会返回None
        """
        # _regex = re.compile(r'\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}')
        m = cls.email_regex.match(text)
        if m:
            return m.group(0)
        else:
            return ''

    @classmethod
    def clean_url(cls, text):
        """
        清晰URl，如果出现http://这种，就去掉，没有就不管,只保留网址部分
        """
        if isinstance(text, str):
            # print '--------------->', text
            outtext = cls.url_regex.sub('', text)
            return outtext

        return text

    @classmethod
    def check_tel_phone(cls, text):
        """
        返回True表示正常，False表示有非法字符
        """
        if isinstance(text, str):
            # print '--------------->%s'%text
            match = cls.tel_regex.match(text)
            if not match:
                return False
            return True

        return False

    @classmethod
    def check_over_sea_tel_phone(cls, text):
        """
        返回True表示正常，False表示有非法字符
        """
        if isinstance(text, str):
            # print '--------------->%s'%text
            match = cls.over_sea_tel_regex.match(text)
            if not match:
                return False
            return True

        return False


word_check = WordCheck()