from datetime import datetime

from flask import jsonify, request
from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import (
    DEFAULT_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
    VALID_STATUSES,
    utc_now,
)


def _task_with_relations(task):
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def list_tasks():
    try:
        tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
        return jsonify([_task_with_relations(task) for task in tasks]), 200
    except Exception:
        return jsonify({'error': 'Erro interno'}), 500


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return jsonify(data), 200


def _parse_due_date(value):
    return datetime.strptime(value, '%Y-%m-%d')


def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    title = data.get('title')
    if not title:
        return jsonify({'error': 'Título é obrigatório'}), 400
    if len(title) < MIN_TITLE_LENGTH:
        return jsonify({'error': 'Título muito curto'}), 400
    if len(title) > MAX_TITLE_LENGTH:
        return jsonify({'error': 'Título muito longo'}), 400

    status = data.get('status', 'pending')
    priority = data.get('priority', DEFAULT_PRIORITY)
    user_id = data.get('user_id')
    category_id = data.get('category_id')

    if status not in VALID_STATUSES:
        return jsonify({'error': 'Status inválido'}), 400
    if priority < 1 or priority > 5:
        return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
    if user_id and not db.session.get(User, user_id):
        return jsonify({'error': 'Usuário não encontrado'}), 404
    if category_id and not db.session.get(Category, category_id):
        return jsonify({'error': 'Categoria não encontrada'}), 404

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if data.get('due_date'):
        try:
            task.due_date = _parse_due_date(data['due_date'])
        except (TypeError, ValueError):
            return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar task'}), 500


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    if 'title' in data:
        if len(data['title']) < MIN_TITLE_LENGTH:
            return jsonify({'error': 'Título muito curto'}), 400
        if len(data['title']) > MAX_TITLE_LENGTH:
            return jsonify({'error': 'Título muito longo'}), 400
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if not task.validate_status(data['status']):
            return jsonify({'error': 'Status inválido'}), 400
        task.status = data['status']

    if 'priority' in data:
        if not task.validate_priority(data['priority']):
            return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not db.session.get(User, data['user_id']):
            return jsonify({'error': 'Usuário não encontrado'}), 404
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not db.session.get(Category, data['category_id']):
            return jsonify({'error': 'Categoria não encontrada'}), 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = _parse_due_date(data['due_date'])
            except (TypeError, ValueError):
                return jsonify({'error': 'Formato de data inválido'}), 400
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = utc_now()

    try:
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar'}), 500


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deletada com sucesso'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500


def search_tasks():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')

    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%'),
            )
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        try:
            tasks = tasks.filter(Task.priority == int(priority))
        except ValueError:
            return jsonify({'error': 'Prioridade inválida'}), 400
    if user_id:
        try:
            tasks = tasks.filter(Task.user_id == int(user_id))
        except ValueError:
            return jsonify({'error': 'Usuário inválido'}), 400

    return jsonify([task.to_dict() for task in tasks.all()]), 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()
    overdue_count = Task.query.filter(
        Task.due_date.isnot(None),
        Task.due_date < utc_now(),
        ~Task.status.in_(['done', 'cancelled']),
    ).count()
    stats = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
    return jsonify(stats), 200
