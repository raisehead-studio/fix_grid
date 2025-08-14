from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from .two_factor import TwoFactorAuth
import json

two_factor_bp = Blueprint('two_factor_bp', __name__)
two_factor_auth = TwoFactorAuth()

@two_factor_bp.route('/api/2fa/setup', methods=['POST'])
@login_required
def setup_2fa():
    """設定 2FA"""
    try:
        # 生成新的密鑰和備用碼
        secret = two_factor_auth.generate_secret()
        backup_codes = two_factor_auth.generate_backup_codes()
        
        # 生成手動設定說明
        totp_uri = two_factor_auth.get_totp_uri(current_user.username, secret)
        setup_instructions = two_factor_auth.generate_setup_instructions(
            current_user.username, secret, totp_uri
        )
        
        # 暫存到 session 中，等待驗證後才正式啟用
        session['pending_2fa'] = {
            'secret': secret,
            'backup_codes': backup_codes,
            'setup_instructions': setup_instructions['content']
        }
        
        return jsonify({
            'status': 'success',
            'setup_instructions': setup_instructions['content'],
            'secret': secret,
            'backup_codes': backup_codes
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@two_factor_bp.route('/api/2fa/force-setup', methods=['POST'])
def force_setup_2fa():
    """強制設定 2FA - 不需要登入驗證"""
    try:
        # 檢查 session 中是否有待設定的用戶資訊
        pending_user = session.get('pending_user')
        if not pending_user:
            return jsonify({'status': 'error', 'message': '請先登入'}), 400
        
        # 生成新的密鑰和備用碼
        secret = two_factor_auth.generate_secret()
        backup_codes = two_factor_auth.generate_backup_codes()
        
        # 生成手動設定說明
        totp_uri = two_factor_auth.get_totp_uri(pending_user['username'], secret)
        setup_instructions = two_factor_auth.generate_setup_instructions(
            pending_user['username'], secret, totp_uri
        )
        
        # 暫存到 session 中，等待驗證後才正式啟用
        session['pending_2fa'] = {
            'secret': secret,
            'backup_codes': backup_codes,
            'setup_instructions': setup_instructions['content']
        }
        
        return jsonify({
            'status': 'success',
            'setup_instructions': setup_instructions['content'],
            'secret': secret,
            'backup_codes': backup_codes
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@two_factor_bp.route('/api/2fa/force-verify', methods=['POST'])
def force_verify_2fa():
    """強制驗證 2FA - 不需要登入驗證"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'status': 'error', 'message': '請輸入驗證碼'}), 400
        
        # 檢查 session 中是否有待設定的 2FA 資訊
        pending_2fa = session.get('pending_2fa')
        pending_user = session.get('pending_user')
        
        if not pending_2fa or not pending_user:
            return jsonify({'status': 'error', 'message': '請先設定 2FA'}), 400
        
        secret = pending_2fa['secret']
        
        # 驗證 TOTP 令牌
        if two_factor_auth.verify_totp(secret, token):
            # 啟用 2FA
            if two_factor_auth.setup_2fa(
                pending_user['id'], 
                secret, 
                pending_2fa['backup_codes']
            ):
                # 清除 session 中的暫存資料
                session.pop('pending_2fa', None)
                session.pop('pending_user', None)
                
                return jsonify({
                    'status': 'success',
                    'message': '2FA 設定成功',
                    'backup_codes': pending_2fa['backup_codes']
                })
            else:
                return jsonify({'status': 'error', 'message': '啟用 2FA 失敗'}), 500
        else:
            return jsonify({'status': 'error', 'message': '驗證碼錯誤'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@two_factor_bp.route('/api/2fa/verify-setup', methods=['POST'])
@login_required
def verify_setup():
    """驗證並完成 2FA 設定"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'status': 'error', 'message': '請輸入驗證碼'}), 400
        
        # 檢查 session 中是否有待設定的 2FA 資訊
        pending_2fa = session.get('pending_2fa')
        if not pending_2fa:
            return jsonify({'status': 'error', 'message': '請先設定 2FA'}), 400
        
        secret = pending_2fa['secret']
        
        # 驗證 TOTP 令牌
        if two_factor_auth.verify_totp(secret, token):
            # 啟用 2FA
            if two_factor_auth.setup_2fa(
                current_user.id, 
                secret, 
                pending_2fa['backup_codes']
            ):
                # 清除 session 中的暫存資料
                session.pop('pending_2fa', None)
                
                return jsonify({
                    'status': 'success',
                    'message': '2FA 設定成功',
                    'backup_codes': pending_2fa['backup_codes']
                })
            else:
                return jsonify({'status': 'error', 'message': '啟用 2FA 失敗'}), 500
        else:
            return jsonify({'status': 'error', 'message': '驗證碼錯誤'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@two_factor_bp.route('/api/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    """停用 2FA"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'status': 'error', 'message': '請輸入密碼'}), 400
        
        # 驗證密碼（這裡需要從 models.py 導入密碼驗證功能）
        from .models import get_user_by_id_with_role
        user = get_user_by_id_with_role(current_user.id)
        
        if not user or not user['password']:
            return jsonify({'status': 'error', 'message': '用戶不存在'}), 404
        
        from werkzeug.security import check_password_hash
        if not check_password_hash(user['password'], password):
            return jsonify({'status': 'error', 'message': '密碼錯誤'}), 400
        
        # 停用 2FA
        if two_factor_auth.disable_2fa(current_user.id):
            return jsonify({'status': 'success', 'message': '2FA 已停用'})
        else:
            return jsonify({'status': 'error', 'message': '停用 2FA 失敗'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@two_factor_bp.route('/api/2fa/status')
@login_required
def get_2fa_status():
    """取得 2FA 狀態"""
    try:
        info = two_factor_auth.get_user_2fa_info(current_user.id)
        if info:
            return jsonify({
                'status': 'success',
                'enabled': info['enabled'],
                'has_backup_codes': len(info['backup_codes']) > 0
            })
        else:
            return jsonify({'status': 'error', 'message': '無法取得 2FA 資訊'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@two_factor_bp.route('/api/2fa/backup-codes')
@login_required
def get_backup_codes():
    """取得備用碼"""
    try:
        info = two_factor_auth.get_user_2fa_info(current_user.id)
        if info and info['enabled']:
            return jsonify({
                'status': 'success',
                'backup_codes': info['backup_codes']
            })
        else:
            return jsonify({'status': 'error', 'message': '2FA 未啟用'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@two_factor_bp.route('/api/2fa/attempts')
@login_required
def get_recent_attempts():
    """取得最近的 2FA 嘗試記錄"""
    try:
        attempts = two_factor_auth.get_recent_attempts(current_user.id)
        return jsonify({
            'status': 'success',
            'attempts': attempts
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@two_factor_bp.route('/api/2fa/verify-login', methods=['POST'])
def verify_login_2fa():
    """驗證登入時的 2FA"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        token = data.get('token')
        backup_code = data.get('backup_code')
        
        if not user_id:
            return jsonify({'status': 'error', 'message': '缺少用戶 ID'}), 400
        
        # 檢查是否啟用 2FA
        if not two_factor_auth.is_2fa_enabled(user_id):
            return jsonify({'status': 'error', 'message': '用戶未啟用 2FA'}), 400
        
        # 取得用戶的 2FA 資訊
        info = two_factor_auth.get_user_2fa_info(user_id)
        if not info:
            return jsonify({'status': 'error', 'message': '無法取得 2FA 資訊'}), 500
        
        ip_address = request.remote_addr
        success = False
        
        # 驗證 TOTP 令牌
        if token and two_factor_auth.verify_totp(info['secret'], token):
            success = True
        # 驗證備用碼
        elif backup_code and two_factor_auth.verify_backup_code(user_id, backup_code):
            success = True
        
        # 記錄嘗試
        two_factor_auth.record_attempt(user_id, ip_address, success)
        
        if success:
            return jsonify({'status': 'success', 'message': '驗證成功'})
        else:
            return jsonify({'status': 'error', 'message': '驗證失敗'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
