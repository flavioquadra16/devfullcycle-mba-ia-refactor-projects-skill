from datetime import timedelta

from flask import jsonify
from sqlalchemy import case, func

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import REPORT_WINDOW_DAYS, calculate_percentage, utc_now


def _status_counts():
    rows = dict(db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all())
    return {
        'pending': rows.get('pending', 0),
        'in_progress': rows.get('in_progress', 0),
        'done': rows.get('done', 0),
        'cancelled': rows.get('cancelled', 0),
    }


def summary_report():
    now = utc_now()
    status_counts = _status_counts()
    priority_rows = dict(
        db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
    )
    overdue_tasks = Task.query.filter(
        Task.due_date.isnot(None),
        Task.due_date < now,
        ~Task.status.in_(['done', 'cancelled']),
    ).all()
    overdue_list = [
        {
            'id': task.id,
            'title': task.title,
            'due_date': str(task.due_date),
            'days_overdue': (now - task.due_date).days,
        }
        for task in overdue_tasks
    ]
    window_start = now - timedelta(days=REPORT_WINDOW_DAYS)
    recent_tasks = Task.query.filter(Task.created_at >= window_start).count()
    recent_done = Task.query.filter(
        Task.status == 'done',
        Task.updated_at >= window_start,
    ).count()

    done_case = case((Task.status == 'done', 1), else_=0)
    productivity = (
        db.session.query(
            User.id,
            User.name,
            func.count(Task.id),
            func.coalesce(func.sum(done_case), 0),
        )
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id, User.name)
        .order_by(User.id)
        .all()
    )
    user_stats = []
    for user_id, name, total, completed in productivity:
        total = int(total or 0)
        completed = int(completed or 0)
        user_stats.append({
            'user_id': user_id,
            'user_name': name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })

    report = {
        'generated_at': str(now),
        'overview': {
            'total_tasks': Task.query.count(),
            'total_users': User.query.count(),
            'total_categories': Category.query.count(),
        },
        'tasks_by_status': status_counts,
        'tasks_by_priority': {
            'critical': priority_rows.get(1, 0),
            'high': priority_rows.get(2, 0),
            'medium': priority_rows.get(3, 0),
            'low': priority_rows.get(4, 0),
            'minimal': priority_rows.get(5, 0),
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }
    return jsonify(report), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    done = pending = in_progress = cancelled = overdue = high_priority = 0
    for task in tasks:
        if task.status == 'done':
            done += 1
        elif task.status == 'pending':
            pending += 1
        elif task.status == 'in_progress':
            in_progress += 1
        elif task.status == 'cancelled':
            cancelled += 1
        if task.priority <= 2:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    total = len(tasks)
    return jsonify({
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': calculate_percentage(done, total),
        },
    }), 200
