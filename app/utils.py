import subprocess
import socket

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
    "two_factor": "雙因素認證管理",
}

def get_real_ip_address():
    """獲取真實的對外 IP 地址"""
    try:
        # 方法 1: 使用 curl ifconfig.me（主要方法）
        try:
            result = subprocess.run(['curl', '-s', 'ifconfig.me'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # 方法 2: 使用 socket 獲取本機 IP（備用方案）
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            pass
        
        # 如果所有方法都失敗，返回預設值
        return "127.0.0.1"
        
    except Exception as e:
        print(f"Error getting real IP: {e}")
        return "127.0.0.1"

def get_client_ip(request):
    """獲取客戶端 IP 地址，優先使用真實對外 IP"""
    try:
        # 優先使用真實對外 IP
        real_ip = get_real_ip_address()
        if real_ip and real_ip != "127.0.0.1":
            return real_ip
        
        # 備用方案：從請求頭獲取
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip_header = request.headers.get('X-Real-IP')
        if real_ip_header:
            return real_ip_header
        
        # 最後使用 remote_addr
        return request.remote_addr or "127.0.0.1"
        
    except Exception as e:
        print(f"Error getting client IP: {e}")
        return "127.0.0.1"

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