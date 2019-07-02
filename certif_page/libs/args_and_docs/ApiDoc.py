from flask_docs import ApiDoc

NO_DOC = '这个Api没有文档'


class FlaskApiDoc(ApiDoc):

    def get_api_name(self, func):
        """e.g. Convert 'do_work' to 'Do Work'"""
        words = func.__name__.split('_')
        words = [w.capitalize() for w in words]
        return ' '.join(words)

    def get_api_doc(self, func):
        if func.__doc__:
            func_modules = func.__module__.split('.')
            obj_name = func.__doc__.split(":::")[1]
            # func_name = func.__name__
            del func_modules[-1]
            func_modules.append('schema')
            # func_modules.append(obj_name)
            try:
                pkg = __import__('.'.join(func_modules))
                del func_modules[0]
                func_modules.append(obj_name)
                schema_cls = pkg
                for name in func_modules:
                    schema_cls = getattr(schema_cls, name)
                schema_obj = schema_cls()
                # json_schema = JSONSchema(nested=True)
                # result = json_schema.dump(schema_obj).data
                func.__doc__ = func.__doc__ + self.assemble_doc(schema_obj)
            except Exception as e:
                pass
            return func.__doc__.replace('\t', '    ')
        else:
            return NO_DOC

    def assemble_doc(self, schema_obj):
        prefix = """
        @@@
        #### args
    
        | 参数 | 可空 | 类型 | 描述 |
        |--------|--------|--------|--------|
        """
        attr_lst = []
        for key in dir(schema_obj):
            if '__' not in key:
                attr_lst.append(key)

        for attr_item in attr_lst:
            try:
                arg = '\t|' + attr_item + '|'
                nullable = ('False' if getattr(schema_obj, attr_item)[0].required else 'True') + '|'
                input_type = getattr(schema_obj, attr_item)[0].__class__.__name__ + '|'
                des = getattr(schema_obj, attr_item)[0].metadata.get('description') + '|\n'
                line = arg + nullable + input_type + des
                prefix = prefix + line
            except Exception as e:
                try:
                    arg = '\t|' + attr_item + '|'
                    nullable = ('False' if getattr(schema_obj, attr_item).required else 'True') + '|'
                    input_type = getattr(schema_obj, attr_item).__class__.__name__ + '|'
                    des = getattr(schema_obj, attr_item).metadata.get('description') + '|\n'
                    line = arg + nullable + input_type + des
                    prefix = prefix + line
                except Exception as e:
                    pass

        postfix = """
        @@@
        """
        return prefix + postfix
