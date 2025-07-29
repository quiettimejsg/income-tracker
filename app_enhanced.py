from flask import Flask, jsonify, request, send_from_directory
from flask_login import LoginManager, login_required, current_user
from flask_cors import CORS
from config import config
from models import db, User
from auth import auth_bp
from transactions import transactions_bp
from categories import categories_bp
from analytics import analytics_bp
from i18n import get_message, get_current_language
import os

def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    
    # 配置CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # 配置登录管理
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.session_protection = 'strong'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({
            'error': get_message('common.unauthorized'),
            'code': 'UNAUTHORIZED'
        }), 401
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(analytics_bp)
    
    # 全局错误处理
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': get_message('common.invalid_request'),
            'code': 'BAD_REQUEST'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({
            'error': get_message('common.unauthorized'),
            'code': 'UNAUTHORIZED'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': get_message('common.forbidden'),
            'code': 'FORBIDDEN'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': get_message('common.not_found'),
            'code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'error': get_message('common.server_error'),
            'code': 'INTERNAL_ERROR'
        }), 500
    
    # API路由
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'language': get_current_language(),
            'supported_languages': [
                'zh', 'en', 'fr', 'es', 'de', 'ja', 'it', 'pt', 'ru', 'ar',
                'ko', 'hi', 'id', 'tr', 'nl', 'pl', 'sv', 'vi', 'th', 'uk'
            ]
        }), 200
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """获取前端配置"""
        return jsonify({
            'app_name': 'Enhanced Income Tracker',
            'version': '2.0.0',
            'supported_languages': [
                'zh', 'en', 'fr', 'es', 'de', 'ja', 'it', 'pt', 'ru', 'ar',
                'ko', 'hi', 'id', 'tr', 'nl', 'pl', 'sv', 'vi', 'th', 'uk'
            ],
            'features': {
                'user_authentication': True,
                'multi_language': True,
                'data_analytics': True,
                'data_export': True,
                'custom_categories': True,
                'transaction_search': True,
                'bulk_operations': True
            }
        }), 200
    
    # 兼容原有API接口
    @app.route('/api/income', methods=['GET'])
    @login_required
    def get_income_legacy():
        """兼容原有的收入获取接口"""
        from transactions import get_transactions
        return get_transactions()
    
    @app.route('/api/income', methods=['POST'])
    @login_required
    def create_income_legacy():
        """兼容原有的收入创建接口"""
        # 将原有的收入记录转换为新的交易记录格式
        data = request.get_json()
        if data:
            # 确保类型为收入
            data['type'] = 'income'
            # 如果没有指定类别，使用默认的"其他收入"类别
            if 'category_id' not in data:
                from models import Category
                default_category = Category.query.filter_by(
                    user_id=current_user.id,
                    name='其他收入',
                    type='income'
                ).first()
                if default_category:
                    data['category_id'] = default_category.id
        
        from transactions import create_transaction
        return create_transaction()
    
    # 静态文件服务
    @app.route('/')
    def index():
        """主页"""
        return send_from_directory('.', 'index.html')
    
    @app.route('/<path:filename>')
    def static_files(filename):
        """静态文件服务"""
        return send_from_directory('.', filename)
    
    # 数据库初始化
    with app.app_context():
        db.create_all()
    
    # 请求前处理
    @app.before_request
    def before_request():
        """请求前处理"""
        # 记录请求语言
        lang = get_current_language()
        request.current_language = lang
    
    # 响应后处理
    @app.after_request
    def after_request(response):
        """响应后处理"""
        # 添加语言头
        if hasattr(request, 'current_language'):
            response.headers['Content-Language'] = request.current_language
        
        # 添加CORS头（如果需要）
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept-Language'
        
        return response
    
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 开发服务器配置
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )

