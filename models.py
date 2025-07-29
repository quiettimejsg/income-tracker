from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    """类别模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' 或 'expense'
    color = db.Column(db.String(7), default='#007bff')  # 颜色代码
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'color': self.color,
            'created_at': self.created_at.isoformat()
        }

class Transaction(db.Model):
    """交易记录模型"""
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' 或 'expense'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'amount': float(self.amount),
            'description': self.description,
            'date': self.date.isoformat(),
            'type': self.type,
            'category': self.category.to_dict() if self.category else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

def init_default_categories(user_id):
    """为新用户初始化默认类别"""
    default_income_categories = [
        {'name': '工资', 'color': '#28a745'},
        {'name': '奖金', 'color': '#17a2b8'},
        {'name': '投资收益', 'color': '#ffc107'},
        {'name': '其他收入', 'color': '#6c757d'}
    ]
    
    default_expense_categories = [
        {'name': '餐饮', 'color': '#dc3545'},
        {'name': '交通', 'color': '#fd7e14'},
        {'name': '购物', 'color': '#e83e8c'},
        {'name': '娱乐', 'color': '#6f42c1'},
        {'name': '医疗', 'color': '#20c997'},
        {'name': '教育', 'color': '#0dcaf0'},
        {'name': '住房', 'color': '#198754'},
        {'name': '其他支出', 'color': '#6c757d'}
    ]
    
    categories = []
    
    # 添加收入类别
    for cat in default_income_categories:
        category = Category(
            name=cat['name'],
            type='income',
            color=cat['color'],
            user_id=user_id
        )
        categories.append(category)
    
    # 添加支出类别
    for cat in default_expense_categories:
        category = Category(
            name=cat['name'],
            type='expense',
            color=cat['color'],
            user_id=user_id
        )
        categories.append(category)
    
    db.session.add_all(categories)
    db.session.commit()
    
    return categories

