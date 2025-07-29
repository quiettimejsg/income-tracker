from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Transaction, Category
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract, and_
from decimal import Decimal
import calendar

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

def get_date_range(period, custom_start=None, custom_end=None):
    """获取日期范围"""
    today = date.today()
    
    if period == 'today':
        return today, today
    elif period == 'week':
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end
    elif period == 'month':
        start = today.replace(day=1)
        end = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        return start, end
    elif period == 'quarter':
        quarter = (today.month - 1) // 3 + 1
        start = date(today.year, (quarter - 1) * 3 + 1, 1)
        if quarter == 4:
            end = date(today.year, 12, 31)
        else:
            end = date(today.year, quarter * 3, calendar.monthrange(today.year, quarter * 3)[1])
        return start, end
    elif period == 'year':
        start = date(today.year, 1, 1)
        end = date(today.year, 12, 31)
        return start, end
    elif period == 'custom':
        if custom_start and custom_end:
            try:
                start = datetime.strptime(custom_start, '%Y-%m-%d').date()
                end = datetime.strptime(custom_end, '%Y-%m-%d').date()
                return start, end
            except ValueError:
                return None, None
    
    return None, None

@analytics_bp.route('/overview', methods=['GET'])
@login_required
def get_overview():
    """获取财务概览"""
    try:
        period = request.args.get('period', 'month')
        custom_start = request.args.get('start_date')
        custom_end = request.args.get('end_date')
        
        start_date, end_date = get_date_range(period, custom_start, custom_end)
        
        if start_date is None or end_date is None:
            return jsonify({'error': '日期范围无效'}), 400
        
        # 获取期间内的收入和支出总额
        income_total = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'income',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar()
        
        expense_total = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar()
        
        # 获取交易数量
        income_count = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'income',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).count()
        
        expense_count = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).count()
        
        # 计算净收入
        net_income = float(income_total) - float(expense_total)
        
        # 获取上一期间的数据用于比较
        period_length = (end_date - start_date).days + 1
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)
        
        prev_income = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'income',
            Transaction.date >= prev_start,
            Transaction.date <= prev_end
        ).scalar()
        
        prev_expense = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            Transaction.date >= prev_start,
            Transaction.date <= prev_end
        ).scalar()
        
        # 计算变化百分比
        income_change = 0
        expense_change = 0
        
        if float(prev_income) > 0:
            income_change = ((float(income_total) - float(prev_income)) / float(prev_income)) * 100
        
        if float(prev_expense) > 0:
            expense_change = ((float(expense_total) - float(prev_expense)) / float(prev_expense)) * 100
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'period_type': period
            },
            'summary': {
                'total_income': float(income_total),
                'total_expense': float(expense_total),
                'net_income': net_income,
                'income_count': income_count,
                'expense_count': expense_count,
                'total_transactions': income_count + expense_count
            },
            'changes': {
                'income_change': round(income_change, 2),
                'expense_change': round(expense_change, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取概览数据失败: {str(e)}'}), 500

@analytics_bp.route('/trends', methods=['GET'])
@login_required
def get_trends():
    """获取趋势数据"""
    try:
        period = request.args.get('period', 'month')
        group_by = request.args.get('group_by', 'day')  # day, week, month
        custom_start = request.args.get('start_date')
        custom_end = request.args.get('end_date')
        
        start_date, end_date = get_date_range(period, custom_start, custom_end)
        
        if start_date is None or end_date is None:
            return jsonify({'error': '日期范围无效'}), 400
        
        # 根据分组方式构建查询
        if group_by == 'day':
            date_format = Transaction.date
            date_label = func.date(Transaction.date)
        elif group_by == 'week':
            date_format = func.date_trunc('week', Transaction.date)
            date_label = func.date_trunc('week', Transaction.date)
        elif group_by == 'month':
            date_format = func.date_trunc('month', Transaction.date)
            date_label = func.date_trunc('month', Transaction.date)
        else:
            date_format = Transaction.date
            date_label = func.date(Transaction.date)
        
        # 获取收入趋势
        income_trends = db.session.query(
            date_label.label('date'),
            func.coalesce(func.sum(Transaction.amount), 0).label('amount')
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'income',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).group_by(date_label).order_by(date_label).all()
        
        # 获取支出趋势
        expense_trends = db.session.query(
            date_label.label('date'),
            func.coalesce(func.sum(Transaction.amount), 0).label('amount')
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).group_by(date_label).order_by(date_label).all()
        
        # 格式化数据
        income_data = []
        expense_data = []
        
        for trend in income_trends:
            income_data.append({
                'date': trend.date.isoformat() if hasattr(trend.date, 'isoformat') else str(trend.date),
                'amount': float(trend.amount)
            })
        
        for trend in expense_trends:
            expense_data.append({
                'date': trend.date.isoformat() if hasattr(trend.date, 'isoformat') else str(trend.date),
                'amount': float(trend.amount)
            })
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'group_by': group_by
            },
            'income_trends': income_data,
            'expense_trends': expense_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取趋势数据失败: {str(e)}'}), 500

@analytics_bp.route('/categories', methods=['GET'])
@login_required
def get_category_analysis():
    """获取类别分析数据"""
    try:
        period = request.args.get('period', 'month')
        transaction_type = request.args.get('type', 'expense')
        custom_start = request.args.get('start_date')
        custom_end = request.args.get('end_date')
        
        if transaction_type not in ['income', 'expense']:
            return jsonify({'error': '类型必须是income或expense'}), 400
        
        start_date, end_date = get_date_range(period, custom_start, custom_end)
        
        if start_date is None or end_date is None:
            return jsonify({'error': '日期范围无效'}), 400
        
        # 获取类别统计
        category_stats = db.session.query(
            Category.id,
            Category.name,
            Category.color,
            func.count(Transaction.id).label('transaction_count'),
            func.coalesce(func.sum(Transaction.amount), 0).label('total_amount')
        ).join(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == transaction_type,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).group_by(Category.id, Category.name, Category.color).order_by(
            func.sum(Transaction.amount).desc()
        ).all()
        
        # 计算总金额用于百分比计算
        total_amount = sum(float(stat.total_amount) for stat in category_stats)
        
        categories_data = []
        for stat in category_stats:
            amount = float(stat.total_amount)
            percentage = (amount / total_amount * 100) if total_amount > 0 else 0
            
            categories_data.append({
                'id': stat.id,
                'name': stat.name,
                'color': stat.color,
                'amount': amount,
                'percentage': round(percentage, 2),
                'transaction_count': stat.transaction_count
            })
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'type': transaction_type
            },
            'total_amount': total_amount,
            'categories': categories_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取类别分析失败: {str(e)}'}), 500

@analytics_bp.route('/monthly-comparison', methods=['GET'])
@login_required
def get_monthly_comparison():
    """获取月度对比数据"""
    try:
        months = int(request.args.get('months', 6))  # 默认显示6个月
        
        if months < 1 or months > 24:
            return jsonify({'error': '月份数量应在1-24之间'}), 400
        
        today = date.today()
        
        monthly_data = []
        
        for i in range(months):
            # 计算月份
            target_date = today.replace(day=1) - timedelta(days=i * 30)
            target_date = target_date.replace(day=1)
            
            # 获取该月的第一天和最后一天
            start_of_month = target_date
            if target_date.month == 12:
                end_of_month = date(target_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_of_month = date(target_date.year, target_date.month + 1, 1) - timedelta(days=1)
            
            # 获取该月的收入和支出
            income = db.session.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            ).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == 'income',
                Transaction.date >= start_of_month,
                Transaction.date <= end_of_month
            ).scalar()
            
            expense = db.session.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            ).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == 'expense',
                Transaction.date >= start_of_month,
                Transaction.date <= end_of_month
            ).scalar()
            
            monthly_data.append({
                'month': f"{target_date.year}-{target_date.month:02d}",
                'year': target_date.year,
                'month_num': target_date.month,
                'income': float(income),
                'expense': float(expense),
                'net': float(income) - float(expense)
            })
        
        # 按时间正序排列
        monthly_data.reverse()
        
        return jsonify({
            'monthly_comparison': monthly_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取月度对比数据失败: {str(e)}'}), 500

@analytics_bp.route('/export', methods=['GET'])
@login_required
def export_data():
    """导出数据"""
    try:
        export_format = request.args.get('format', 'csv')
        period = request.args.get('period', 'month')
        custom_start = request.args.get('start_date')
        custom_end = request.args.get('end_date')
        
        if export_format not in ['csv', 'json']:
            return jsonify({'error': '导出格式必须是csv或json'}), 400
        
        start_date, end_date = get_date_range(period, custom_start, custom_end)
        
        if start_date is None or end_date is None:
            return jsonify({'error': '日期范围无效'}), 400
        
        # 获取交易数据
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).order_by(Transaction.date.desc()).all()
        
        if export_format == 'json':
            data = {
                'export_info': {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'export_date': datetime.utcnow().isoformat(),
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    }
                },
                'transactions': [t.to_dict() for t in transactions]
            }
            return jsonify(data), 200
        
        else:  # CSV格式
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入标题行
            writer.writerow([
                'ID', '日期', '类型', '类别', '金额', '描述', '创建时间'
            ])
            
            # 写入数据行
            for transaction in transactions:
                writer.writerow([
                    transaction.id,
                    transaction.date.isoformat(),
                    '收入' if transaction.type == 'income' else '支出',
                    transaction.category.name if transaction.category else '',
                    float(transaction.amount),
                    transaction.description or '',
                    transaction.created_at.isoformat()
                ])
            
            csv_data = output.getvalue()
            output.close()
            
            return jsonify({
                'csv_data': csv_data,
                'filename': f'transactions_{start_date}_{end_date}.csv'
            }), 200
        
    except Exception as e:
        return jsonify({'error': f'导出数据失败: {str(e)}'}), 500

