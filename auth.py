from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, init_default_categories
from i18n import get_message
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 6:
        return False, get_message('auth.weak_password')
    if not re.search(r'[A-Za-z]', password):
        return False, get_message('auth.weak_password')
    if not re.search(r'[0-9]', password):
        return False, get_message('auth.weak_password')
    return True, get_message('common.success')

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请提供注册信息'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # 验证输入
        if not username or not email or not password:
            return jsonify({'error': get_message('auth.username_required')}), 400
        
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': get_message('auth.username_required')}), 400
        
        if not validate_email(email):
            return jsonify({'error': get_message('auth.invalid_email')}), 400
        
        is_valid, msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': msg}), 400
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': get_message('auth.user_exists')}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': get_message('auth.email_exists')}), 409
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # 为新用户初始化默认类别
        init_default_categories(user.id)
        
        return jsonify({
            'message': get_message('auth.register_success'),
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请提供登录信息'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username) | (User.email == username.lower())
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 登录用户
        login_user(user, remember=True)
        session.permanent = True
        
        return jsonify({
            'message': '登录成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    try:
        logout_user()
        session.clear()
        return jsonify({'message': '登出成功'}), 200
    except Exception as e:
        return jsonify({'error': f'登出失败: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """获取当前用户信息"""
    try:
        return jsonify({
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取用户信息失败: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请提供密码信息'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': '当前密码和新密码不能为空'}), 400
        
        # 验证当前密码
        if not current_user.check_password(current_password):
            return jsonify({'error': '当前密码错误'}), 401
        
        # 验证新密码
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': msg}), 400
        
        # 更新密码
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': '密码修改成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'密码修改失败: {str(e)}'}), 500

