# Django 学习记录 原型界面开发学习记录
根据需求在func_process_app/page_function文件夹中以要求的***页面名字***创建对应的文件夹

## 一.统计区
### 函数get_flow_statistics(**kwargs)      返回统一格式
```
db_helper = DBHelper()             #创建一个数据库连接管理器
session = db_helper.get_session()  #获取一个可用的数据库会话
result = {"code": ReturnEnum.ER_FAIL().code, "msg": ReturnEnum.ER_FAIL().msg, "data": {}}  ##设置默认查询失败
try:
    statistics_res = session.query(TLargeItemInvoicingManagement.stepNo, func.count(TLargeItemInvoicingManagement.id)).group_by(
        TLargeItemInvoicingManagement.stepNo).all()    ##按节点号分组，统计每个节点号的id数量
    a_flow_step_statistics = []
    setSum = 0
    for stepNo, count in statistics_res:
        a_flow_step_statistics.append({'s_node_name': stepNo, 'i_count': count})
        setSum += count   ##统计所有节点号的id数量
    a_flow_step_statistics.append({'s_node_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.all_step.value, 'i_count': setSum})   ##其对应设置在ConstEnum中
    data = {'a_flow_step_statistics': a_flow_step_statistics}
    result.update({"code": ReturnEnum.ER_SUCCESS().code, "msg": ReturnEnum.ER_SUCCESS().msg, "data": data})  ##按照指定格式输出并返回查询成功
except Exception as e:
    result.update({"code": ReturnEnum.ER_FAIL().code, "msg": str(e), "data": {}})
finally:
    db_helper.close_session()
return result
```
类似消息99+？

## 二.数据区
约定俗称
i_xxx = int整数类型数据 (如: i_id, i_total_number)
o_xxx = obj对象类型数据 (如: o_basic_info, o_buyer_information)
a_xxx = arr数组类型数据 (如: a_data_list, a_project_information_amount)
s_xxx = str字符串类型数据 (如: s_user_name, s_serial_number)
b_xxx = bool布尔类型数据 (如: b_is_html, b_is_active)
### data_interface_area(分页参数，特殊参数，条件参数，**kwargs)  ##在原型页面设计会有对应的参数
其中对于result的更新使用updata而非赋值是因为操作仅对部分值进行修改

在使用get_filter搜索了相关字段其中SQLAlchemy的链式查询，所以sq中的约束是一层一层的递增的之间的关系是AND，最终组成符合查询
```
if e_supplier_name_large:
        sq = get_filter(sq=sq, model_field=TLargeItemInvoicingManagement.supplier_name,
                        value=e_supplier_name_large.strip())   ##strip()来保持数据一致，删除字符串前后无用的信息
if s_customs_declaration:
        sq = get_page_filter(sq=sq, model_field=TLargeItemInvoicingManagement.customs_declaration_num,
                            value=s_customs_declaration.strip(),
                            query_type=dt.get('s_customs_declaration', QueryType.ALL_TYPE.value))
if s_company_name:
        sq = get_page_filter(sq=sq, model_field=TLargeItemInvoicingManagement.unit_name,
                            value=s_company_name.strip(),
                            query_type=dt.get('s_company_name', QueryType.ALL_TYPE.value))
if s_business_serial_no:
        sq = get_page_filter(sq=sq, model_field=TLargeItemInvoicingManagement.serial_number,
                            value=s_business_serial_no.strip(),
                            query_type=dt.get('s_business_serial_no', QueryType.ALL_TYPE.value))
if s_node_name and str(s_node_name).strip() != str(P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.all_step.value):
        sq = sq.filter(TLargeItemInvoicingManagement.stepNo == s_node_name) 
```
## 三.流程按钮
```
@staticmethod
    def process_button_area_jump(a_id, original_step, target_step, remark_need=False, **kwargs):
        
        """
        流程按钮区跳转
        :param a_id: 数据ID列表
        :param original_step: 原流程setpNo
        :param target_step: 新stepNo
        :param remark_need: 是否添加备注
        :param kwargs:
        :return:
        """

        result = {"code": ReturnEnum.ER_FAIL().code, "msg": ReturnEnum.ER_FAIL().msg, "data": dict()}
        if not a_id:
            return {"code": ReturnEnum.ER_LACK_PARAMETER().code, "msg": ReturnEnum.ER_LACK_PARAMETER().msg, "data": dict()}
        if not isinstance(a_id, list):
            return {"code": ReturnEnum.ER_RISK_PARAM_ERROR().code, "msg": ReturnEnum.ER_RISK_PARAM_ERROR().msg, "data": dict()}
        # if len(a_id) > BigZHCG.one.value:
        #     return {'code': ReturnEnum.ER_FAIL().code, 'msg': u'失败,不允许一次操作多条数据!'}
        s_remarks = kwargs.get('s_remarks', '')
        if remark_need and not s_remarks:
            return {"code": ReturnEnum.ER_LACK_PARAMETER().code, "msg": '备注必填', "data": dict()}
        if len(str(s_remarks)) > P_FL_RETENTION_HANDLE.REMARK_LIMIT.value:
            return {"code": ReturnEnum.ER_RISK_PARAM_ERROR().code, "msg": '备注不超过500字符', "data": dict()}

        db_helper = DBHelper()
        session = db_helper.get_session()
        try:
            data_list_all = session.query(TLargeItemInvoicingManagement).filter(TLargeItemInvoicingManagement.id.in_(a_id)).all()    ## 查看所要查找的id是否都在TLargeItemInvoicingManagement
            if len(data_list_all) != len(set(a_id)):
                return {"code": ReturnEnum.ER_NO_DATA().code, "msg": ReturnEnum.ER_NO_DATA().msg}
            data_list = session.query(TLargeItemInvoicingManagement).filter(TLargeItemInvoicingManagement.id.in_(a_id),
                                                                         TLargeItemInvoicingManagement.stepNo == original_step).all()
            if len(data_list) != len(set(a_id)):
                return {"code": ReturnEnum.ER_DATA_STATUS_CHANGED().code, "msg": ReturnEnum.ER_DATA_STATUS_CHANGED().msg, "data": dict()}
            s_user_name_cn = kwargs.get('s_user_name_cn', REPLACE_NULL_VALUES.NOT_FOUND.value)
            step_dict = P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.online_step_dict.value
            for data_obj in data_list:
                data_obj.stepNo = target_step
                data_obj.data_update_time = datetime.now()
                Flow().add_jump_record_log(
                    s_app_label_name=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_app_label_name.value,
                    s_model_name=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_model_name.value,
                    i_id=data_obj.id,
                    s_field_label=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.stepNo.value,
                    s_old_value=str(original_step),
                    s_new_value=str(target_step),
                    s_login_name=s_user_name_cn,
                    remark=s_remarks
                )
                # 新增供应商系统日志
                if original_step in [
                        P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.dkp_step.value,
                        P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.cwqr_step.value
                ] and target_step == P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.fq_step.value:
                    Flow().add_jump_record_log(
                        s_app_label_name=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_app_label_name.value,
                        s_model_name=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.supplier_s_model_name.value,
                        i_id=data_obj.id,
                        s_field_label=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.stepNo.value,
                        s_old_value=str(step_dict.get(original_step, '')),
                        s_new_value=str(step_dict.get(target_step, '')),
                        s_login_name=s_user_name_cn,
                        remark=s_remarks
                    )
                if original_step == P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.dsh_step.value and target_step == P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.dkp_step.value:
                    Flow().add_jump_record_log(
                        s_app_label_name=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_app_label_name.value,
                        s_model_name=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.supplier_s_model_name.value,
                        i_id=data_obj.id,
                        s_field_label=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.stepNo.value,
                        s_old_value=str(step_dict.get(target_step, '')),
                        s_new_value=str(step_dict.get(target_step, '')),
                        s_login_name=s_user_name_cn,
                        remark=s_remarks
                    )
            session.commit()
            return {"code": ReturnEnum.ER_SUCCESS().code, "msg": '操作成功', "data": dict()}
        except Exception as e:
            import traceback
            traceback.print_exc()
            session.rollback()
            result["code"] = ReturnEnum.ER_SERVER_ERROR().code
            result["msg"] = str(e)
        finally:
            db_helper.close_session()
        return result
```


# 原型界面开发流程

## 需要准备的数据
1.table下的db.model的字段映射
2.ConstEnum 中配置相关流程对应的setpNO，以及映射



### 一.数据搜索区  data_interface_area（i_page，i_page_size（用于计算偏移量）,s_node_name，a_field_query_type(特殊参数)，所需要展示参数，**kwargs）：  

### 常见的错误避免：  
```
result = {"code": ReturnEnum.ER_FAIL().code, "msg": ReturnEnum.ER_FAIL().msg, "data": dict()}  
if not i_page or not i_page_size:  
    result.update({"code": ReturnEnum.ER_LACK_PARAMETER().code, "msg": ReturnEnum.ER_LACK_PARAMETER().msg})  
    return result  
if isinstance(a_field_query_type, list):  
    for o_field_query_type in a_field_query_type:  
        if not isinstance(o_field_query_type, dict):  
            result.update(  
                {'code': ReturnEnum.ER_RISK_PARAM_ERROR().code, 'msg': ReturnEnum.ER_RISK_PARAM_ERROR().msg})
            return result  
else:  
    result.update({'code': ReturnEnum.ER_RISK_PARAM_ERROR().code, 'msg': ReturnEnum.ER_RISK_PARAM_ERROR().msg})
    return result   
```
### 会话建立：  
```
db_helper = DBHelper()  
session = db_helper.get_session()  

try： 
    offsets = (i_page - 1) * i_page_size  
    sq = session.query(TLargeItemInvoicingManagement)  ## 查询构建器  
    dt = {}  ## 将列表转化成字典    
    for o_field_query_type in a_field_query_type:  ## <font color="red">a_field_query_type在get_flow_statistics</font>  
        key = o_field_query_type.get("s_field_label")  
        value = o_field_query_type.get("e_common_query_type")  
        dt[key] = value  
```
### 链式查询：

##开始链式查询有需要特殊查询整或与的使用get_page_filter，其他使用get_filter
```
if s_customs_declaration:
    sq = get_page_filter(sq=sq,model_field=TLargeItemInvoicingManagement.customs_declaration_num,
        value=s_customs_declaration.strip(),
        query_type=dt.get('s_customs_declaration', QueryType.ALL_TYPE.value)) ## 默认是整
if s_company_name:
    sq = get_filter(sq=sq,model_field=TLargeItemInvoicingManagement.unit_name,value=s_company_name.strip())
if s_business_serial_no:
    sq = get_page_filter(sq=sq,model_field=TLargeItemInvoicingManagement.serial_number,
        value=s_business_serial_no.strip(),
        query_type=dt.get('s_business_serial_no', QueryType.ALL_TYPE.value))
if e_supplier_name_large:
    sq = get_page_filter(sq=sq,model_field=TLargeItemInvoicingManagement.supplier_name,
        value=e_supplier_name_large.strip(),
        query_type=dt.get('e_supplier_name_large', QueryType.ALL_TYPE.value))
if s_node_name and str(s_node_name).strip() != str(P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.all_step):
    sq = sq.get_filter(TLargeItemInvoicingManagement.stepNo == s_node_name)

count = sq.count()  ## 统计查询结果的数量
select_data = sq.order_by(TLargeItemInvoicingManagement.id.desc()).offset(offsets).limit(i_page_size).all()  ## 把数据按降序进行排序
```
全局函数注入
最后按要求分装返回函数
```
except Exception as e:  
    result.update({"code": ReturnEnum.ER_SERVER_ERROR().code, "msg": str(traceback.format_exc())})  
finally:  
    db_helper.close_session()  
return result  
```
### 二.统计区  get_flow_statistics(**kwargs)
```
db_helper = DBHelper()
session = db_helper.get_session()
res = {"code": ReturnEnum.ER_FAIL().code, "msg": ReturnEnum.ER_FAIL().msg, "data": dict()}
try:
    statistics_res = session.query(TLargeItemInvoicingManagement.stepNo,func.count(TLargeItemInvoicingManagement.id)).group_by(TLargeItemInvoicingManagement.stepNo).all()
    a_flow_step_statistics = []    ###怎么传入到data_interface_area中
    sum = 0
    for stepNo, count in statistics_res:
        a_flow_step_statistics.append({'s_node_name': stepNo, 'i_count': count})
        sum += count
    a_flow_step_statistics.append({'s_node_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.all_step.value, 'i_count': sum})
except Exception as e:
    res = {"code": ReturnEnum.ER_FAIL().code, "msg": str(e), "data": dict()}
finally:
    db_helper.close_session()
return res
```

### 三.按钮跳转区 process_button_area_jump(a_id, original_step, target_step, remark_need=False, **kwargs)  ##<font color="red">a_id，以及kwargs的疑问</font>
所谓的跳转是将订单信息进行状态的转变，并且转变后提交到数据库，所以需要对应操作的日志以及回滚操作来保证代码的健壮性
### 常见错误校验
```
result = {"code": ReturnEnum.ER_FAIL().code, "msg": ReturnEnum.ER_FAIL().msg, "data": dict()}
        #要求a_id必须是列表
        if not a_id:
            return {"code": ReturnEnum.ER_LACK_PARAMETER().code, "msg": ReturnEnum.ER_LACK_PARAMETER().msg, "data": dict()}
        if not isinstance(a_id, list):
            return {"code": ReturnEnum.ER_RISK_PARAM_ERROR().code, "msg": ReturnEnum.ER_RISK_PARAM_ERROR().msg, "data": dict()}
        
        s_remarks = kwargs.get('s_remarks', '')  ##Kwargs的内容从何判断
        if remark_need and not s_remarks:
            return {"code": ReturnEnum.ER_LACK_PARAMETER().code, "msg": '备注必填', "data": dict()}
        if len(str(s_remarks)) > P_FL_RETENTION_HANDLE.REMARK_LIMIT.value:
            return {"code": ReturnEnum.ER_RISK_PARAM_ERROR().code, "msg": '备注不超过500字符', "data": dict()}
```
### 构建对话
```
db_helper = DBHepler()
session = db_helper.get_session()
try:
    data_list_all = session.query(TLargeItemInvoicingManagement).filter(TLargeItemInvoicingManagement.id.in_(a_id)).all()
    if len(data_list_all) != len(set(a_id)): ## 存在不在数据库中的数据id
        return {"code": ReturnEnum.ER_NO_DATA().code, "msg": ReturnEnum.ER_NO_DATA().msg}
    data_list = session.query(TLargeItemInvoicingManagement).filter(TLargeItemInvoicingManagement.id.in_(a_id),
                                                                    TLargeItemInvoicingManagement.stepNo == original_step).all()
    if len(data_list) != len(set(a_id)):  ## 存在不属于数据库中流程的id
        return {"code": ReturnEnum.ER_DATA_STATUS_CHANGED().code, "msg": ReturnEnum.ER_DATA_STATUS_CHANGED().msg, "data": dict()}
    ## 日志记录
    for data_obj in data_list:
        data_obj.stepNo = target_step  ## 修改状态
        data_obj.data_update_time = datetime.now()
        Flow().add_jump_record_log(
            s_app_label_name=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_app_label_name.value,
            s_model_name=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_model_name.value,
            i_id=data_obj.id,
            s_field_label=P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.stepNo.value,
            s_old_value=str(original_step),
            s_new_value=str(target_step),
            s_login_name=kwargs.get('s_user_name_cn', REPLACE_NULL_VALUES.NOT_FOUND.value),
        )
    session.commit()
    return {"code": ReturnEnum.ER_SUCCESS().code, "msg": '操作成功', "data": dict()}
except Exception as e:
    import traceback
    traceback.print_exc()  #打印当前异常的详细堆栈信息
    session.rollback()
    result["code"] = ReturnEnum.ER_SERVER_ERROR().code
    result["msg"] = str(e)
finally:
    db_helper.close_session()
return result        
```

### 问题
1.class定义后下的方法中obj指代什么搜索所出来的数据库信息？那么谁又回去搜索
在注册表中将模型与obj对应
2.看起来没有调用，定义这些class谁来执行呢？
自定义管理界面类   Django Admin 框架自动调用：Django Admin 通过反射机制，根据 list_display 中的方法名自动调用 ：只要方法名在 list_display 中，Django 就会自动调用
3.# 模型类名：驼峰命名，对应数据库表名什么意思
4.get_list_queryset这个方法来获取url


# 全局函数开发流程学习
其接口定义在setting中funchub_service_url   
其属性 定义在# func_process_app/table/t_public_function_model.py 可以在hq_db中t_public_function_source_config表中找到全局函数的相关信息 
其url属性定义了其所在文件的位置 可以通过`SELECT url, function_name FROM t_public_function WHERE id = XXX;`来查找
run_global_function 中改用原生js可以提高性能

全托管什么意思，只需要调用就可以了？数据会自己更新？

导入from func_process_app.lib.decorator.interceptor import async_run_global_function
在调用的时候
示例：需要传入id，以及入参
```
rt += async_run_global_function([{  
            'function_id': 139320,  
            'param_list': {  
                'i_id': obj.id,  
                'b_is_html': True,  
            }  
        }])
```

从表中数据变成全局函数大致流程：  
1. 通过function_id获取全局函数的id，页面放置占位符（后端输出 HTML 片段）async_run_global_function(func_list, ...)，返回一个带加载图标的占位符，内含接口地址和函数入参   
async_run_global_function 通过以下步骤找到全局函数： 
function_id → 查询 t_public_function 表  
获取配置 → 得到 function_name 和 url  
路径转换 → 通过数据库查询将SVN路径转换为Python模块路径  
动态导入 → 使用 importlib 动态导入模块和函数  
执行函数 → 调用对应的函数并返回结果  

接口地址默认取 GLOBAL_FUNCTION_SERVICE_URL（由环境决定，开发/测试本机为 localhost:10901）。  
2.前端扫描占位符并发起请求 页面加载或滚动时，前端脚本找出所有 .async-run-global-function 元素，按“可视区域 + 并发<=10”策略，解码 data-func-list 并逐个发起请求（axios.post）  
3.后端接收请求并执行对应函数  
+ 前端命中接口：/function/run_global_function（GLOBAL_FUNCTION_SERVICE_URL + "/function/run_global_function"）。  
+ 服务端入口：execute_function.run_global_function。  它会：  
    + 解析 function_id/param_list；  
    + 通过 TPublicFunction 查到函数“文件路径 + 函数名”，动态导入；
    + 执行函数并“规范化返回”，重点是构造成 data.s_html（兼容老返回的 html 或 *_html）。  

tips:  
+ 若函数本身只返回“数据”，不带 s_html，则前端不会直接显示。通常会封一个“渲染型全局函数”（示例：ASINFunc.asin_sale_info_new(..., b_is_html=True)）把数据转成 s_html 再返回。
+ 通过 get_svn_url_by_function_id/get_function_obj 完成 “function_id → 模块路径/函数名 → 函数对象” 的定位与调用。
4.前端拿到 s_html 并插入页面  成功返回后，前端把 data.s_html 插入到占位符前，并隐藏加载图标。


全局函数执行 D:\project\fancyqube\func_process_app\function\execute_function.py

由于异步渲染的顺序怎么确定的前后的？还是说异步仅仅是于同步的异步，异步与异步之间还是有顺序的
ans：并无严格的顺序看请求的顺序来渲染

R2025040860285
思路从供应商采购合同信息中获取‘合同超期天数’，从海外仓采购计划基本信息获取‘供应商名称’找到其对应的id 还要找到对应的计划号为空的不要。
对应的全局函数D:\project\fancyqube\func_process_app\class_function\PurchaseFunc.py

### 前置准备
在软件规范的全局页面函数中找到相关单子的信息(若没找到可以找亮哥（孙金亮）建立)
在对应的全局函数中配置相关信息
明确所需要用到的db


D:\project\fancyqube\func_process_app\page_function\P_large_order_manage.py 全局函数调用应该在这里
CGOrderLarge::get_cg_contract_overdue_days 传入采购单号返回超期天数
```
def get_cg_contract_overdue_days(s_cg_order_no: str, s_sku: str = '', **kwargs):
        """
        如果只传入 s_cg_order_no 则获取的是该采购单的合同交付超期天数
        如果传入 s_cg_order_no s_sku 则获取的是该采购单下SKU的合同交付超期天数
        """
```
InterfaceFunction().get_function_desc()

获取参数名称
1. 调用 InterfaceFunction().get_function_desc('Purchase::supplier_procurement_contract')  
   ↓  
2. 查询数据库 TPublicFunction 表获取函数ID  
   ↓  
3. 根据函数ID查询 TPublicFunctionParam 和 TPublicParam 表  
   ↓  
4. 构建 o_interface_function_param 字典  
   ↓  
5. 返回包含中文参数名的数据  
   ↓  
6. 在HTML生成时使用中文名称作为表格标题  

## 供应商交期延误信息
目前已经开发出来了
但是速度太慢初步判断是CGOrderLarge::get_cg_contract_overdue_days 方法的反复调用导致的时间太慢
