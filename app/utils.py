page_name_map = {
    "manage_accounts": "帳號管理",
    "manage_roles": "角色管理",
    "profile": "個人資料",
    "power_outage": "停電彙整表（表一）",
    "water_outage": "停水彙整表（表二）",
    "taiwater_power_outage": "台水公司停電彙整表（表三）",
    "taipower_support": "台電支援需求彙整表（表四）",
    "power_stats": "停電彙整統計表（表五）",
    "water_stats": "停水彙整統計表（表六）",
    "taiwater_disaster": "台水公司災害通報彙整（表七）",
}

def check_page_permission(page, role_name, all_permissions):
    """檢查用戶是否有權限存取指定頁面"""
    role_pages = all_permissions.get(role_name, {})
    return page in role_pages

def check_page_view_permission(page, role_name, all_permissions):
    """檢查用戶是否有權限查看指定頁面（需要 view 權限）"""
    role_pages = all_permissions.get(role_name, {})
    page_permissions = role_pages.get(page, [])
    return 'view' in page_permissions

def require_role(min_role_id):
    """權限檢查裝飾器"""
    from functools import wraps
    from flask import abort
    from flask_login import current_user
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role_id > min_role_id:
                abort(403)  # 權限不足
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_permission(permission):
    """特定權限檢查裝飾器"""
    from functools import wraps
    from flask import abort
    from flask_login import current_user
    from .models import get_role_page_permissions_from_db
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            # 檢查用戶是否有特定權限
            all_permissions = get_role_page_permissions_from_db()
            role_pages = all_permissions.get(current_user.role_name, {})
            user_permissions = []
            for page_permissions in role_pages.values():
                user_permissions.extend(page_permissions)
            
            if permission not in user_permissions:
                abort(403)  # 權限不足
            return f(*args, **kwargs)
        return decorated_function
    return decorator