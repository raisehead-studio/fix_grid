from flask import Blueprint, request, jsonify
from .ip_lockout import IPLockoutManager

ip_lockout_bp = Blueprint('ip_lockout_bp', __name__)
ip_lockout_manager = IPLockoutManager()

@ip_lockout_bp.route('/api/ip-lockout/status')
def get_ip_lockout_status():
    """獲取當前 IP 的鎖定狀態"""
    try:
        ip_address = request.remote_addr
        lockout_info = ip_lockout_manager.get_lockout_info(ip_address)
        
        if lockout_info:
            return jsonify({
                'status': 'success',
                'ip_address': ip_address,
                'is_locked': lockout_info['is_locked'],
                'failed_attempts': lockout_info['failed_attempts'],
                'remaining_attempts': lockout_info['remaining_attempts'],
                'locked_until': lockout_info['locked_until'],
                'last_failed_at': lockout_info['last_failed_at']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '無法獲取鎖定狀態'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@ip_lockout_bp.route('/api/ip-lockout/unlock', methods=['POST'])
def unlock_ip():
    """手動解除 IP 鎖定（管理員功能）"""
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')
        
        if not ip_address:
            return jsonify({
                'status': 'error',
                'message': '請提供 IP 地址'
            }), 400
        
        # 這裡可以添加管理員權限檢查
        # 暫時允許所有請求解除鎖定
        
        # 強制解除鎖定並重置所有記錄
        if ip_lockout_manager.force_unlock_ip(ip_address):
            return jsonify({
                'status': 'success',
                'message': f'IP {ip_address} 已完全解除鎖定並重置失敗記錄'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'解除 IP {ip_address} 鎖定失敗'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@ip_lockout_bp.route('/api/ip-lockout/stats')
def get_lockout_stats():
    """獲取鎖定統計資訊（管理員功能）"""
    try:
        # 這裡可以添加管理員權限檢查
        # 暫時允許所有請求查看統計
        
        # 獲取所有鎖定記錄
        conn = ip_lockout_manager.db_path
        # 這裡可以實現統計功能
        
        return jsonify({
            'status': 'success',
            'message': '統計功能開發中'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
