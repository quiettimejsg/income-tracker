from flask import request
import json
import os

class I18n:
    """国际化支持类"""
    
    def __init__(self):
        self.translations = {}
        self.default_language = 'en'
        self.supported_languages = [
            'zh', 'en', 'fr', 'es', 'de', 'ja', 'it', 'pt', 'ru', 'ar', 
            'ko', 'hi', 'id', 'tr', 'nl', 'pl', 'sv', 'vi', 'th', 'uk'
        ]
        self.load_translations()
    
    def load_translations(self):
        """加载翻译文件"""
        # 后端API消息翻译
        self.translations = {
            'zh': {
                'auth': {
                    'register_success': '注册成功',
                    'login_success': '登录成功',
                    'logout_success': '登出成功',
                    'password_changed': '密码修改成功',
                    'invalid_credentials': '用户名或密码错误',
                    'user_exists': '用户名已存在',
                    'email_exists': '邮箱已被注册',
                    'weak_password': '密码强度不够',
                    'invalid_email': '邮箱格式不正确',
                    'username_required': '用户名不能为空',
                    'password_required': '密码不能为空',
                    'current_password_wrong': '当前密码错误'
                },
                'transactions': {
                    'created': '交易记录创建成功',
                    'updated': '交易记录更新成功',
                    'deleted': '交易记录删除成功',
                    'not_found': '交易记录不存在',
                    'amount_required': '金额不能为空',
                    'amount_invalid': '金额格式不正确',
                    'date_required': '日期不能为空',
                    'date_invalid': '日期格式不正确',
                    'category_required': '类别不能为空',
                    'category_not_found': '类别不存在',
                    'type_invalid': '类型必须是income或expense'
                },
                'categories': {
                    'created': '类别创建成功',
                    'updated': '类别更新成功',
                    'deleted': '类别删除成功',
                    'not_found': '类别不存在',
                    'name_required': '类别名称不能为空',
                    'name_exists': '该类型下已存在同名类别',
                    'has_transactions': '无法删除类别，还有交易记录使用此类别',
                    'color_invalid': '颜色格式不正确'
                },
                'common': {
                    'success': '操作成功',
                    'error': '操作失败',
                    'invalid_request': '请求数据无效',
                    'unauthorized': '未授权访问',
                    'forbidden': '禁止访问',
                    'not_found': '资源不存在',
                    'server_error': '服务器内部错误',
                    'validation_error': '数据验证失败'
                }
            },
            'en': {
                'auth': {
                    'register_success': 'Registration successful',
                    'login_success': 'Login successful',
                    'logout_success': 'Logout successful',
                    'password_changed': 'Password changed successfully',
                    'invalid_credentials': 'Invalid username or password',
                    'user_exists': 'Username already exists',
                    'email_exists': 'Email already registered',
                    'weak_password': 'Password is too weak',
                    'invalid_email': 'Invalid email format',
                    'username_required': 'Username is required',
                    'password_required': 'Password is required',
                    'current_password_wrong': 'Current password is incorrect'
                },
                'transactions': {
                    'created': 'Transaction created successfully',
                    'updated': 'Transaction updated successfully',
                    'deleted': 'Transaction deleted successfully',
                    'not_found': 'Transaction not found',
                    'amount_required': 'Amount is required',
                    'amount_invalid': 'Invalid amount format',
                    'date_required': 'Date is required',
                    'date_invalid': 'Invalid date format',
                    'category_required': 'Category is required',
                    'category_not_found': 'Category not found',
                    'type_invalid': 'Type must be income or expense'
                },
                'categories': {
                    'created': 'Category created successfully',
                    'updated': 'Category updated successfully',
                    'deleted': 'Category deleted successfully',
                    'not_found': 'Category not found',
                    'name_required': 'Category name is required',
                    'name_exists': 'Category with this name already exists',
                    'has_transactions': 'Cannot delete category with existing transactions',
                    'color_invalid': 'Invalid color format'
                },
                'common': {
                    'success': 'Operation successful',
                    'error': 'Operation failed',
                    'invalid_request': 'Invalid request data',
                    'unauthorized': 'Unauthorized access',
                    'forbidden': 'Access forbidden',
                    'not_found': 'Resource not found',
                    'server_error': 'Internal server error',
                    'validation_error': 'Data validation failed'
                }
            },
            'fr': {
                'auth': {
                    'register_success': 'Inscription réussie',
                    'login_success': 'Connexion réussie',
                    'logout_success': 'Déconnexion réussie',
                    'password_changed': 'Mot de passe modifié avec succès',
                    'invalid_credentials': 'Nom d\'utilisateur ou mot de passe invalide',
                    'user_exists': 'Le nom d\'utilisateur existe déjà',
                    'email_exists': 'Email déjà enregistré',
                    'weak_password': 'Le mot de passe est trop faible',
                    'invalid_email': 'Format d\'email invalide',
                    'username_required': 'Le nom d\'utilisateur est requis',
                    'password_required': 'Le mot de passe est requis',
                    'current_password_wrong': 'Le mot de passe actuel est incorrect'
                },
                'transactions': {
                    'created': 'Transaction créée avec succès',
                    'updated': 'Transaction mise à jour avec succès',
                    'deleted': 'Transaction supprimée avec succès',
                    'not_found': 'Transaction non trouvée',
                    'amount_required': 'Le montant est requis',
                    'amount_invalid': 'Format de montant invalide',
                    'date_required': 'La date est requise',
                    'date_invalid': 'Format de date invalide',
                    'category_required': 'La catégorie est requise',
                    'category_not_found': 'Catégorie non trouvée',
                    'type_invalid': 'Le type doit être revenu ou dépense'
                },
                'categories': {
                    'created': 'Catégorie créée avec succès',
                    'updated': 'Catégorie mise à jour avec succès',
                    'deleted': 'Catégorie supprimée avec succès',
                    'not_found': 'Catégorie non trouvée',
                    'name_required': 'Le nom de la catégorie est requis',
                    'name_exists': 'Une catégorie avec ce nom existe déjà',
                    'has_transactions': 'Impossible de supprimer une catégorie avec des transactions existantes',
                    'color_invalid': 'Format de couleur invalide'
                },
                'common': {
                    'success': 'Opération réussie',
                    'error': 'Opération échouée',
                    'invalid_request': 'Données de requête invalides',
                    'unauthorized': 'Accès non autorisé',
                    'forbidden': 'Accès interdit',
                    'not_found': 'Ressource non trouvée',
                    'server_error': 'Erreur interne du serveur',
                    'validation_error': 'Échec de la validation des données'
                }
            },
            'es': {
                'auth': {
                    'register_success': 'Registro exitoso',
                    'login_success': 'Inicio de sesión exitoso',
                    'logout_success': 'Cierre de sesión exitoso',
                    'password_changed': 'Contraseña cambiada exitosamente',
                    'invalid_credentials': 'Usuario o contraseña inválidos',
                    'user_exists': 'El nombre de usuario ya existe',
                    'email_exists': 'Email ya registrado',
                    'weak_password': 'La contraseña es muy débil',
                    'invalid_email': 'Formato de email inválido',
                    'username_required': 'El nombre de usuario es requerido',
                    'password_required': 'La contraseña es requerida',
                    'current_password_wrong': 'La contraseña actual es incorrecta'
                },
                'transactions': {
                    'created': 'Transacción creada exitosamente',
                    'updated': 'Transacción actualizada exitosamente',
                    'deleted': 'Transacción eliminada exitosamente',
                    'not_found': 'Transacción no encontrada',
                    'amount_required': 'El monto es requerido',
                    'amount_invalid': 'Formato de monto inválido',
                    'date_required': 'La fecha es requerida',
                    'date_invalid': 'Formato de fecha inválido',
                    'category_required': 'La categoría es requerida',
                    'category_not_found': 'Categoría no encontrada',
                    'type_invalid': 'El tipo debe ser ingreso o gasto'
                },
                'categories': {
                    'created': 'Categoría creada exitosamente',
                    'updated': 'Categoría actualizada exitosamente',
                    'deleted': 'Categoría eliminada exitosamente',
                    'not_found': 'Categoría no encontrada',
                    'name_required': 'El nombre de la categoría es requerido',
                    'name_exists': 'Ya existe una categoría con este nombre',
                    'has_transactions': 'No se puede eliminar una categoría con transacciones existentes',
                    'color_invalid': 'Formato de color inválido'
                },
                'common': {
                    'success': 'Operación exitosa',
                    'error': 'Operación fallida',
                    'invalid_request': 'Datos de solicitud inválidos',
                    'unauthorized': 'Acceso no autorizado',
                    'forbidden': 'Acceso prohibido',
                    'not_found': 'Recurso no encontrado',
                    'server_error': 'Error interno del servidor',
                    'validation_error': 'Fallo en la validación de datos'
                }
            },
            'de': {
                'auth': {
                    'register_success': 'Registrierung erfolgreich',
                    'login_success': 'Anmeldung erfolgreich',
                    'logout_success': 'Abmeldung erfolgreich',
                    'password_changed': 'Passwort erfolgreich geändert',
                    'invalid_credentials': 'Ungültiger Benutzername oder Passwort',
                    'user_exists': 'Benutzername existiert bereits',
                    'email_exists': 'E-Mail bereits registriert',
                    'weak_password': 'Passwort ist zu schwach',
                    'invalid_email': 'Ungültiges E-Mail-Format',
                    'username_required': 'Benutzername ist erforderlich',
                    'password_required': 'Passwort ist erforderlich',
                    'current_password_wrong': 'Aktuelles Passwort ist falsch'
                },
                'transactions': {
                    'created': 'Transaktion erfolgreich erstellt',
                    'updated': 'Transaktion erfolgreich aktualisiert',
                    'deleted': 'Transaktion erfolgreich gelöscht',
                    'not_found': 'Transaktion nicht gefunden',
                    'amount_required': 'Betrag ist erforderlich',
                    'amount_invalid': 'Ungültiges Betragsformat',
                    'date_required': 'Datum ist erforderlich',
                    'date_invalid': 'Ungültiges Datumsformat',
                    'category_required': 'Kategorie ist erforderlich',
                    'category_not_found': 'Kategorie nicht gefunden',
                    'type_invalid': 'Typ muss Einkommen oder Ausgabe sein'
                },
                'categories': {
                    'created': 'Kategorie erfolgreich erstellt',
                    'updated': 'Kategorie erfolgreich aktualisiert',
                    'deleted': 'Kategorie erfolgreich gelöscht',
                    'not_found': 'Kategorie nicht gefunden',
                    'name_required': 'Kategoriename ist erforderlich',
                    'name_exists': 'Kategorie mit diesem Namen existiert bereits',
                    'has_transactions': 'Kategorie mit vorhandenen Transaktionen kann nicht gelöscht werden',
                    'color_invalid': 'Ungültiges Farbformat'
                },
                'common': {
                    'success': 'Operation erfolgreich',
                    'error': 'Operation fehlgeschlagen',
                    'invalid_request': 'Ungültige Anfragedaten',
                    'unauthorized': 'Unbefugter Zugriff',
                    'forbidden': 'Zugriff verboten',
                    'not_found': 'Ressource nicht gefunden',
                    'server_error': 'Interner Serverfehler',
                    'validation_error': 'Datenvalidierung fehlgeschlagen'
                }
            },
            'ja': {
                'auth': {
                    'register_success': '登録が成功しました',
                    'login_success': 'ログインが成功しました',
                    'logout_success': 'ログアウトが成功しました',
                    'password_changed': 'パスワードが正常に変更されました',
                    'invalid_credentials': 'ユーザー名またはパスワードが無効です',
                    'user_exists': 'ユーザー名は既に存在します',
                    'email_exists': 'メールアドレスは既に登録されています',
                    'weak_password': 'パスワードが弱すぎます',
                    'invalid_email': '無効なメール形式です',
                    'username_required': 'ユーザー名は必須です',
                    'password_required': 'パスワードは必須です',
                    'current_password_wrong': '現在のパスワードが間違っています'
                },
                'transactions': {
                    'created': '取引が正常に作成されました',
                    'updated': '取引が正常に更新されました',
                    'deleted': '取引が正常に削除されました',
                    'not_found': '取引が見つかりません',
                    'amount_required': '金額は必須です',
                    'amount_invalid': '無効な金額形式です',
                    'date_required': '日付は必須です',
                    'date_invalid': '無効な日付形式です',
                    'category_required': 'カテゴリは必須です',
                    'category_not_found': 'カテゴリが見つかりません',
                    'type_invalid': 'タイプは収入または支出である必要があります'
                },
                'categories': {
                    'created': 'カテゴリが正常に作成されました',
                    'updated': 'カテゴリが正常に更新されました',
                    'deleted': 'カテゴリが正常に削除されました',
                    'not_found': 'カテゴリが見つかりません',
                    'name_required': 'カテゴリ名は必須です',
                    'name_exists': 'この名前のカテゴリは既に存在します',
                    'has_transactions': '既存の取引があるカテゴリは削除できません',
                    'color_invalid': '無効な色形式です'
                },
                'common': {
                    'success': '操作が成功しました',
                    'error': '操作が失敗しました',
                    'invalid_request': '無効なリクエストデータです',
                    'unauthorized': '未承認のアクセスです',
                    'forbidden': 'アクセスが禁止されています',
                    'not_found': 'リソースが見つかりません',
                    'server_error': 'サーバー内部エラーです',
                    'validation_error': 'データ検証に失敗しました'
                }
            }
        }
        
        # 为其他语言添加英文作为后备
        for lang in self.supported_languages:
            if lang not in self.translations:
                self.translations[lang] = self.translations['en']
    
    def get_language(self):
        """获取当前请求的语言"""
        # 从请求头获取语言
        lang = request.headers.get('Accept-Language', self.default_language)
        
        # 从查询参数获取语言（优先级更高）
        lang = request.args.get('lang', lang)
        
        # 从JSON数据获取语言（最高优先级）
        if request.is_json:
            data = request.get_json(silent=True)
            if data and 'lang' in data:
                lang = data['lang']
        
        # 处理语言代码（取前两位）
        if lang and '-' in lang:
            lang = lang.split('-')[0]
        
        # 验证语言是否支持
        if lang not in self.supported_languages:
            lang = self.default_language
        
        return lang
    
    def get_message(self, key_path, lang=None):
        """获取翻译消息"""
        if lang is None:
            lang = self.get_language()
        
        # 获取翻译
        translation = self.translations.get(lang, self.translations[self.default_language])
        
        # 按路径获取消息
        keys = key_path.split('.')
        message = translation
        
        for key in keys:
            if isinstance(message, dict) and key in message:
                message = message[key]
            else:
                # 如果找不到翻译，使用英文作为后备
                fallback = self.translations[self.default_language]
                for fallback_key in keys:
                    if isinstance(fallback, dict) and fallback_key in fallback:
                        fallback = fallback[fallback_key]
                    else:
                        return key_path  # 如果连英文都没有，返回键路径
                return fallback
        
        return message if isinstance(message, str) else key_path

# 全局实例
i18n = I18n()

def get_message(key_path, lang=None):
    """获取翻译消息的便捷函数"""
    return i18n.get_message(key_path, lang)

def get_current_language():
    """获取当前语言的便捷函数"""
    return i18n.get_language()

