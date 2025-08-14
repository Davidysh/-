import statistics
from pandas import offsets
from func_process_app.common_function.sqlalchemy_sesssion import DBHelper
from brick.public.ReturnEnum import ReturnEnum
from func_process_app.table.hq_db.t_large_item_invoicing_management import TLargeItemInvoicingManagement       ##在table以及对应的表中，配置相关的表名，字段名，索引等
from sqlalchemy import func
from brick.public.ConstEnum import P_FL_LARGE_ITEM_INVOICING_MANAGEMENT,ArabNumber
from func_process_app.function.common import get_page_filter, get_filter  ##基本过滤和整或与过滤
from func_process_app.lib.decorator.interceptor import async_run_global_function  ##异步执行全局函数
from brick.public.ConstEnum import QueryType, PublicValueConfig, P_FL_RETENTION_HANDLE, REPLACE_NULL_VALUES, P_FL_LARGE_ITEM_INVOICING_MANAGEMENT
import traceback
from func_process_app.class_function.FlowFunc import Flow
from datetime import datetime

class P_FL_large_item_invoicing_management_0(object):
    @staticmethod
    def get_flow_statistics(**kwargs):  ##统计区，计节点的数据
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
            a_flow_step_statistics.append({'s_node_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.all_step.value, 'i_count': setSum})   ##其流程节点设置在ConstEnum中
            data = {'a_flow_step_statistics': a_flow_step_statistics}
            result.update({"code": ReturnEnum.ER_SUCCESS().code, "msg": ReturnEnum.ER_SUCCESS().msg, "data": data})  ##按照指定格式输出并返回查询成功
        except Exception as e:
            result.update({"code": ReturnEnum.ER_FAIL().code, "msg": str(e), "data": {}})
        finally:
            db_helper.close_session()
        return result

    @staticmethod
    def data_interface_area(i_page, i_page_size, s_node_name, a_field_query_type,
                            s_customs_declaration, e_supplier_name_large, s_company_name, s_business_serial_no, **kwargs):
        """
        大件开票管理流程:待核对::数据区接口::数据区接口
        """

        result = {"code": ReturnEnum.ER_FAIL().code, "msg": ReturnEnum.ER_FAIL().msg, "data": dict()}
        if not i_page or not i_page_size:
            result.update({"code": ReturnEnum.ER_LACK_PARAMETER().code, "msg": ReturnEnum.ER_LACK_PARAMETER().msg})   ##缺少必要参数
            return result
        if isinstance(a_field_query_type, list):  ##判断a_field_query_type是否为列表
            for o_field_query_type in a_field_query_type:
                if not isinstance(o_field_query_type, dict):  ##且列表内存的是字典
                    result.update(
                        {'code': ReturnEnum.ER_RISK_PARAM_ERROR().code, 'msg': ReturnEnum.ER_RISK_PARAM_ERROR().msg})  ##传入参数格式错误
                    return result
        else:
            result.update({'code': ReturnEnum.ER_RISK_PARAM_ERROR().code, 'msg': ReturnEnum.ER_RISK_PARAM_ERROR().msg})
            return result
        db_helper = DBHelper()
        session = db_helper.get_session()
        try:
            offset = (i_page - 1) * i_page_size  
            sq = session.query(TLargeItemInvoicingManagement)
            dt = {o_field_query_type.get("s_field_label"): o_field_query_type.get("e_common_query_type") for
                o_field_query_type in a_field_query_type}
            ## 搜索了相关字段并且SQLAlchemy的链式查询
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

            count = sq.order_by(TLargeItemInvoicingManagement.id.desc()).count()
            select_data = sq.order_by(TLargeItemInvoicingManagement.id.desc()).offset(offset).limit(i_page_size).all()  ## offset设置的了偏差值
            formatted_results = []
            for data in select_data:
                #  大件开票基本信
                o_basic_info_large_item_invoicing = async_run_global_function(
                    [{
                        'function_id': 143921,
                        'param_list': {
                            's_business_serial_no': data.serial_number,
                            'b_is_html': True,
                        }
                    }]
                )
                # 购买方人信息
                o_buyer_information = async_run_global_function(
                    [{
                        'function_id': 143918,
                        'param_list': {
                            's_uuid': data.unit_serial_number,
                            'b_is_html': True,
                        }
                    }]
                )
                # 项目信息及金额
                a_project_information_amount = async_run_global_function(
                    [{
                        'function_id': 143919,
                        'param_list': {
                            's_business_serial_no': data.detail_serial_number,
                            's_customs_declaration': data.customs_declaration_num,
                            'b_is_html': True,
                        }
                    }]
                )

                a_remark_comment = async_run_global_function([{
                    'function_id': 140326,
                    'param_list': {'s_app_label_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_app_label_name.value,
                                's_model_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_model_name.value,
                                's_field_label': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_field_label.value,
                                's_serial_number': data.id,
                                'box_width': '220px',
                                'b_is_html': True,
                                's_login_name': kwargs.get('s_user_name_cn'),
                                's_jump_to_url': f'https://sup.fancyqube.net/Project/admin/func_process_app/t_large_component_suppliers_invoicing/?page_name=P_FL_large_component_suppliers_invoicing_4&s_business_serial_no={data.serial_number}',
                                'select_moren': '{},{}'.format(data.creator, data.supplier_name),
                                's_is_systems': PublicValueConfig.SUPPLIER_SYS.value,
                                's_remark_comment_flag': 'remark',
                                }}])
                # 操作日志
                a_flow_operation_log = async_run_global_function(
                    [{
                        'function_id': 11841,
                        'param_list': {
                            's_app_label_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_app_label_name.value,
                            's_model_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_model_name.value,
                            's_field_label': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.stepNo.value,
                            'i_id': data.id,
                            'b_is_html': True,
                        }
                    }]
                )

                ##按原型页面要求分装返回参数  也就是页面所展示的数据
                formatted_results.append({
                    "i_id": data.id,
                    "o_basic_info_large_item_invoicing": o_basic_info_large_item_invoicing,
                    "o_buyer_information": o_buyer_information,
                    "a_project_information_amount": a_project_information_amount,
                    "a_remark_comment": a_remark_comment,
                    "a_flow_operation_log": a_flow_operation_log,
                })
            result = ReturnEnum.ER_SUCCESS().to_dict()
            result['data'] = {'i_total_number': count, 'a_data_list': formatted_results}
        except Exception as e:
            result.update({"code": ReturnEnum.ER_SERVER_ERROR().code, "msg": str(traceback.format_exc())})
        finally:
            db_helper.close_session()
        return result

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
            data_list_all = session.query(TLargeItemInvoicingManagement).filter(TLargeItemInvoicingManagement.id.in_(a_id)).all()   ## 查看是否a_id都在TLargeItemInvoicingManagement都在则长度一定一致
            if len(data_list_all) != len(set(a_id)):
                return {"code": ReturnEnum.ER_NO_DATA().code, "msg": ReturnEnum.ER_NO_DATA().msg}
            data_list = session.query(TLargeItemInvoicingManagement).filter(TLargeItemInvoicingManagement.id.in_(a_id),
                                                                         TLargeItemInvoicingManagement.stepNo == original_step).all()
            if len(data_list) != len(set(a_id)):
                return {"code": ReturnEnum.ER_DATA_STATUS_CHANGED().code, "msg": ReturnEnum.ER_DATA_STATUS_CHANGED().msg, "data": dict()}
            s_user_name_cn = kwargs.get('s_user_name_cn', REPLACE_NULL_VALUES.NOT_FOUND.value)
            step_dict = P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.online_step_dict.value
            for data_obj in data_list:
                data_obj.stepNo = target_step   ##更新流程状态
                data_obj.data_update_time = datetime.now()
                # 添加流程跳转记录日志
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


class P_FL_large_item_invoicing_management_1(object):
    def data_interface_area(i_page,i_page_size,s_node_name,a_field_query_type,s_customs_declaration, e_supplier_name_large, s_company_name, s_business_serial_no,**kwargs): 
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
        db_helper = DBHelper()
        session = db_helper.get_session()
        try:
            offsets = (i_page - 1) * i_page_size
            sq = session.query(TLargeItemInvoicingManagement)  ## 查询构建器
            dt = {}  ## 将列表转化成字典
            for o_field_query_type in a_field_query_type:   ## a_field_query_type是前端传入的查询条件
                key = o_field_query_type.get("s_field_label")  ##查询标签
                value = o_field_query_type.get("e_common_query_type")  ##查询类型
                dt[key] = value
            ## 开始链式查询有需要特殊查询整或与的使用get_page_filter，其他使用get_filter
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
            select_data = sq.order_by(TLargeItemInvoicingManagement.id.desc()).offset(offsets).limit(i_page_size).all()
            formatted_results = []
            for data in select_data:  ## 全局函数调用
                o_basic_info_large_item_invoicing = async_run_global_function(
                    [{
                        'function_id': 143921,
                        'param_list': {
                            's_business_serial_no': data.serial_number,
                            'b_is_html': True,
                        }
                    }]
                )
                # 购买方人信息
                o_buyer_information = async_run_global_function(
                    [{
                        'function_id': 143918,
                        'param_list': {
                            's_uuid': data.unit_serial_number,
                            'b_is_html': True,
                        }
                    }]
                )
                # 项目信息及金额
                a_project_information_amount = async_run_global_function(
                    [{
                        'function_id': 143919,
                        'param_list': {
                            's_business_serial_no': data.detail_serial_number,
                            's_customs_declaration': data.customs_declaration_num,
                            'b_is_html': True,
                        }
                    }]
                )

                a_remark_comment = async_run_global_function([{
                    'function_id': 140326,
                    'param_list': {'s_app_label_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_app_label_name.value,
                                   's_model_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_model_name.value,
                                   's_field_label': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_field_label.value,
                                   's_serial_number': data.id,
                                   'box_width': '220px',
                                   'b_is_html': True,
                                   's_login_name': kwargs.get('s_user_name_cn'),
                                   's_jump_to_url': f'https://sup.fancyqube.net/Project/admin/func_process_app/t_large_component_suppliers_invoicing/?page_name=P_FL_large_component_suppliers_invoicing_4&s_business_serial_no={data.serial_number}',
                                   'select_moren': '{},{}'.format(data.creator, data.supplier_name),
                                   's_is_systems': PublicValueConfig.SUPPLIER_SYS.value,
                                   's_remark_comment_flag': 'remark',
                                   }}])
                # 操作日志
                a_flow_operation_log = async_run_global_function(
                    [{
                        'function_id': 11841,
                        'param_list': {
                            's_app_label_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_app_label_name.value,
                            's_model_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.s_model_name.value,
                            's_field_label': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.stepNo.value,
                            'i_id': data.id,
                            'b_is_html': True,
                        }
                    }]
                )
                formatted_results.append({
                    "i_id": data.id,
                    "o_basic_info_large_item_invoicing": o_basic_info_large_item_invoicing,
                    "o_buyer_information": o_buyer_information,
                    "a_project_information_amount": a_project_information_amount,
                    "a_remark_comment": a_remark_comment,
                    "a_flow_operation_log": a_flow_operation_log,
                })
            ## 查询成功
            result = ReturnEnum.ER_SUCCESS().to_dict()
            result['data'] = {'i_total_number': count, 'a_data_list': formatted_results}
        except Exception as e:
            result.update({"code": ReturnEnum.ER_SERVER_ERROR().code, "msg": str(traceback.format_exc())})
        finally:
            db_helper.close_session()
        return result

    def get_flow_statistics(**kwargs):
        db_helper = DBHelper()
        session = db_helper.get_session()
        try:
            result = session.query(TLargeItemInvoicingManagement.stepNo, func.count(TLargeItemInvoicingManagement.id)).group_by(TLargeItemInvoicingManagement.stepNo).all()
            a_flow_step_statistics = []
            sum = ArabNumber.ZERO   ##为什么不知直接用0
            for stepno, count in result:
                a_flow_step_statistics.append({'s_node_name': stepno, 'i_count': count}, )
                sum += count
            a_flow_step_statistics.append(
                {'s_node_name': P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.all_step.value, 'i_count': sum})
            data = {'a_flow_step_statistics': a_flow_step_statistics}
            res = {"code": ReturnEnum.ER_SUCCESS().code, "msg": "操作成功!", "data": data}
        except Exception as e:
            res = {"code": ReturnEnum.ER_FAIL().code, "msg": str(e), "data": dict()}
        finally:
            db_helper.close_session()
        return res

    def process_button_area_jump(a_id,original_step,target_step,remark_need=False,**kwargs):  
        result = {"code": ReturnEnum.ER_FAIL().code, "msg": ReturnEnum.ER_FAIL().msg, "data": dict()}
        if not a_id:
            return {"code": ReturnEnum.ER_LACK_PARAMETER().code, "msg": ReturnEnum.ER_LACK_PARAMETER().msg, "data": dict()}
        if not isinstance(a_id, list):
            return {"code": ReturnEnum.ER_RISK_PARAM_ERROR().code, "msg": ReturnEnum.ER_RISK_PARAM_ERROR().msg, "data": dict()}
        s_remarks = kwargs.get('s_remarks', '')
        if remark_need and not s_remarks:
            return {"code": ReturnEnum.ER_LACK_PARAMETER().code, "msg": '备注必填', "data": dict()}
        if len(str(s_remarks)) > P_FL_RETENTION_HANDLE.REMARK_LIMIT.value:
            return {"code": ReturnEnum.ER_RISK_PARAM_ERROR().code, "msg": '备注不超过500字符', "data": dict()}
        db_helper = DBHelper()
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


    def process_button_area_jump_to_1_button(a_id,**kwargs):
        original_step = P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.dsh_step.value
        target_step = P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.dkp_step.value
        return P_FL_large_item_invoicing_management_0.process_button_area_jump(a_id,original_step,target_step,remark_need=False,**kwargs)

    def process_button_area_jump_to_4_button(a_id,**kwargs):
        original_step = P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.dsh_step.value
        target_step = P_FL_LARGE_ITEM_INVOICING_MANAGEMENT.fq_step.value
        return P_FL_large_item_invoicing_management_0.process_button_area_jump(a_id,original_step,target_step,remark_need=True,**kwargs)
