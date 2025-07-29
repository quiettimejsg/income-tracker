from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Category, Transaction
import re

categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

def validate_category_data(data, is_update=False):
    """验证类别数据"""
    errors = []
    
    # 验证名称
    name = data.get('name', '').strip()
    if not name and not is_update:
        errors.append('类别名称不能为空')
    elif name:
        if len(name) < 1 or len(name) > 50:
            errors.append('类别名称长度应在1-50个字符之间')
    
    # 验证类型
    category_type = data.get('type')
    if category_type is None and not is_update:
        errors.append('类别类型不能为空')
    elif category_type is not None and category_type not in ['income', 'expense']:
        errors.append('类别类型必须是income或expense')
    
    # 验证颜色
    color = data.get('color', '').strip()
    if color:
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            errors.append('颜色格式不正确，应为#RRGGBB格式')
    
    return errors

@categories_bp.route('', methods=['GET'])
@login_required
def get_categories():
    """获取用户的所有类别"""
    try:
        category_type = request.args.get('type')
        
        query = Category.query.filter_by(user_id=current_user.id)
        
        if category_type in ['income', 'expense']:
            query = query.filter_by(type=category_type)
        
        categories = query.order_by(Category.type, Category.name).all()
        
        return jsonify({
            'categories': [cat.to_dict() for cat in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取类别失败: {str(e)}'}), 500

@categories_bp.route('', methods=['POST'])
@login_required
def create_category():
    """创建新类别"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请提供类别数据'}), 400
        
        # 验证数据
        errors = validate_category_data(data)
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400
        
        name = data['name'].strip()
        category_type = data['type']
        color = data.get('color', '#007bff').strip()
        
        # 检查同类型下是否已存在同名类别
        existing = Category.query.filter_by(
            user_id=current_user.id,
            name=name,
            type=category_type
        ).first()
        
        if existing:
            return jsonify({'error': f'该类型下已存在名为"{name}"的类别'}), 409
        
        # 创建类别
        category = Category(
            name=name,
            type=category_type,
            color=color,
            user_id=current_user.id
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': '类别创建成功',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建类别失败: {str(e)}'}), 500

@categories_bp.route('/<int:category_id>', methods=['GET'])
@login_required
def get_category(category_id):
    """获取单个类别"""
    try:
        category = Category.query.filter_by(
            id=category_id,
            user_id=current_user.id
        ).first()
        
        if not category:
            return jsonify({'error': '类别不存在'}), 404
        
        return jsonify({
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取类别失败: {str(e)}'}), 500

@categories_bp.route('/<int:category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    """更新类别"""
    try:
        category = Category.query.filter_by(
            id=category_id,
            user_id=current_user.id
        ).first()
        
        if not category:
            return jsonify({'error': '类别不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供更新数据'}), 400
        
        # 验证数据
        errors = validate_category_data(data, is_update=True)
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400
        
        # 检查名称冲突
        if 'name' in data:
            name = data['name'].strip()
            existing = Category.query.filter_by(
                user_id=current_user.id,
                name=name,
                type=category.type
            ).filter(Category.id != category_id).first()
            
            if existing:
                return jsonify({'error': f'该类型下已存在名为"{name}"的类别'}), 409
            
            category.name = name
        
        if 'color' in data:
            category.color = data['color'].strip()
        
        # 注意：不允许修改类别类型，因为这会影响已有的交易记录
        
        db.session.commit()
        
        return jsonify({
            'message': '类别更新成功',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新类别失败: {str(e)}'}), 500

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    """删除类别"""
    try:
        category = Category.query.filter_by(
            id=category_id,
            user_id=current_user.id
        ).first()
        
        if not category:
            return jsonify({'error': '类别不存在'}), 404
        
        # 检查是否有关联的交易记录
        transaction_count = Transaction.query.filter_by(
            category_id=category_id,
            user_id=current_user.id
        ).count()
        
        if transaction_count > 0:
            return jsonify({
                'error': f'无法删除类别，还有{transaction_count}条交易记录使用此类别'
            }), 409
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': '类别删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除类别失败: {str(e)}'}), 500

@categories_bp.route('/<int:category_id>/transactions', methods=['GET'])
@login_required
def get_category_transactions(category_id):
    """获取类别下的交易记录"""
    try:
        category = Category.query.filter_by(
            id=category_id,
            user_id=current_user.id
        ).first()
        
        if not category:
            return jsonify({'error': '类别不存在'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        pagination = Transaction.query.filter_by(
            category_id=category_id,
            user_id=current_user.id
        ).order_by(Transaction.date.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        transactions = [t.to_dict() for t in pagination.items]
        
        return jsonify({
            'category': category.to_dict(),
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
        return jsonify({'error': f'获取类别交易记录失败: {str(e)}'}), 500

@categories_bp.route('/stats', methods=['GET'])
@login_required
def get_categories_stats():
    """获取类别统计信息"""
    try:
        from sqlalchemy import func
        
        # 获取每个类别的交易统计
        stats = db.session.query(
            Category.id,
            Category.name,
            Category.type,
            Category.color,
            func.count(Transaction.id).label('transaction_count'),
            func.coalesce(func.sum(Transaction.amount), 0).label('total_amount')
        ).outerjoin(Transaction).filter(
            Category.user_id == current_user.id
        ).group_by(Category.id).all()
        
        categories_stats = []
        for stat in stats:
            categories_stats.append({
                'id': stat.id,
                'name': stat.name,
                'type': stat.type,
                'color': stat.color,
                'transaction_count': stat.transaction_count,
                'total_amount': float(stat.total_amount)
            })
        
        return jsonify({
            'categories_stats': categories_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取类别统计失败: {str(e)}'}), 500

