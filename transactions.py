from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Transaction, Category
from i18n import get_message
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from sqlalchemy import and_, or_, desc, asc

transactions_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

def validate_transaction_data(data, is_update=False):
    """验证交易数据"""
    errors = []
    
    # 验证金额
    amount = data.get('amount')
    if amount is None and not is_update:
        errors.append(get_message('transactions.amount_required'))
    elif amount is not None:
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                errors.append(get_message('transactions.amount_invalid'))
            elif amount > Decimal('999999999.99'):
                errors.append(get_message('transactions.amount_invalid'))
        except (InvalidOperation, ValueError):
            errors.append(get_message('transactions.amount_invalid'))
    
    # 验证日期
    transaction_date = data.get('date')
    if transaction_date is None and not is_update:
        errors.append(get_message('transactions.date_required'))
    elif transaction_date is not None:
        try:
            datetime.strptime(transaction_date, '%Y-%m-%d')
        except ValueError:
            errors.append(get_message('transactions.date_invalid'))
    
    # 验证类型
    transaction_type = data.get('type')
    if transaction_type is None and not is_update:
        errors.append(get_message('transactions.type_invalid'))
    elif transaction_type is not None and transaction_type not in ['income', 'expense']:
        errors.append(get_message('transactions.type_invalid'))
    
    # 验证类别
    category_id = data.get('category_id')
    if category_id is None and not is_update:
        errors.append(get_message('transactions.category_required'))
    elif category_id is not None:
        try:
            category_id = int(category_id)
            category = Category.query.filter_by(
                id=category_id, 
                user_id=current_user.id
            ).first()
            if not category:
                errors.append(get_message('transactions.category_not_found'))
            elif transaction_type and category.type != transaction_type:
                errors.append(get_message('transactions.type_invalid'))
        except (ValueError, TypeError):
            errors.append(get_message('transactions.category_not_found'))
    
    # 验证描述
    description = data.get('description', '')
    if len(description) > 200:
        errors.append(get_message('common.validation_error'))
    
    return errors

@transactions_bp.route('', methods=['GET'])
@login_required
def get_transactions():
    """获取交易记录列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        transaction_type = request.args.get('type')
        category_id = request.args.get('category_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'date')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 构建查询
        query = Transaction.query.filter_by(user_id=current_user.id)
        
        # 类型筛选
        if transaction_type in ['income', 'expense']:
            query = query.filter_by(type=transaction_type)
        
        # 类别筛选
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # 日期范围筛选
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Transaction.date >= start_date)
            except ValueError:
                return jsonify({'error': '开始日期格式不正确'}), 400
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Transaction.date <= end_date)
            except ValueError:
                return jsonify({'error': '结束日期格式不正确'}), 400
        
        # 搜索
        if search:
            query = query.filter(
                or_(
                    Transaction.description.contains(search),
                    Transaction.amount.like(f'%{search}%')
                )
            )
        
        # 排序
        if sort_by == 'date':
            order_column = Transaction.date
        elif sort_by == 'amount':
            order_column = Transaction.amount
        elif sort_by == 'created_at':
            order_column = Transaction.created_at
        else:
            order_column = Transaction.date
        
        if sort_order == 'asc':
            query = query.order_by(asc(order_column))
        else:
            query = query.order_by(desc(order_column))
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        transactions = [t.to_dict() for t in pagination.items]
        
        return jsonify({
            'transactions': transactions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取交易记录失败: {str(e)}'}), 500

@transactions_bp.route('', methods=['POST'])
@login_required
def create_transaction():
    """创建交易记录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请提供交易数据'}), 400
        
        # 验证数据
        errors = validate_transaction_data(data)
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400
        
        # 创建交易记录
        transaction = Transaction(
            amount=Decimal(str(data['amount'])),
            description=data.get('description', ''),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            type=data['type'],
            category_id=data['category_id'],
            user_id=current_user.id
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': '交易记录创建成功',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建交易记录失败: {str(e)}'}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
@login_required
def get_transaction(transaction_id):
    """获取单个交易记录"""
    try:
        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=current_user.id
        ).first()
        
        if not transaction:
            return jsonify({'error': '交易记录不存在'}), 404
        
        return jsonify({
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取交易记录失败: {str(e)}'}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
@login_required
def update_transaction(transaction_id):
    """更新交易记录"""
    try:
        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=current_user.id
        ).first()
        
        if not transaction:
            return jsonify({'error': '交易记录不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供更新数据'}), 400
        
        # 验证数据
        errors = validate_transaction_data(data, is_update=True)
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400
        
        # 更新字段
        if 'amount' in data:
            transaction.amount = Decimal(str(data['amount']))
        if 'description' in data:
            transaction.description = data['description']
        if 'date' in data:
            transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'type' in data:
            transaction.type = data['type']
        if 'category_id' in data:
            transaction.category_id = data['category_id']
        
        transaction.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': '交易记录更新成功',
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新交易记录失败: {str(e)}'}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    """删除交易记录"""
    try:
        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=current_user.id
        ).first()
        
        if not transaction:
            return jsonify({'error': '交易记录不存在'}), 404
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': '交易记录删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除交易记录失败: {str(e)}'}), 500

@transactions_bp.route('/bulk-delete', methods=['POST'])
@login_required
def bulk_delete_transactions():
    """批量删除交易记录"""
    try:
        data = request.get_json()
        if not data or 'ids' not in data:
            return jsonify({'error': '请提供要删除的交易记录ID列表'}), 400
        
        ids = data['ids']
        if not isinstance(ids, list) or not ids:
            return jsonify({'error': 'ID列表格式不正确'}), 400
        
        # 验证所有ID都属于当前用户
        transactions = Transaction.query.filter(
            Transaction.id.in_(ids),
            Transaction.user_id == current_user.id
        ).all()
        
        if len(transactions) != len(ids):
            return jsonify({'error': '部分交易记录不存在或无权限删除'}), 400
        
        # 批量删除
        for transaction in transactions:
            db.session.delete(transaction)
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功删除{len(transactions)}条交易记录'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'批量删除失败: {str(e)}'}), 500

