from sqladmin import ModelView
from src.models.user import User
from src.models.team import Team
from src.models.task import Task
from src.models.meeting import Meeting
from src.models.evaluation import Evaluation
from src.models.comment import Comment


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    category = "👥 Персонал"
    icon = "fa-solid fa-user"

    column_list = [User.id, User.email, User.role, User.team_id, User.is_active]
    column_labels = {
        User.id: "ID",
        User.email: "Электронная почта",
        User.role: "Роль",
        User.team_id: "ID Команды",
        User.is_active: "Активен",
    }


class TeamAdmin(ModelView, model=Team):
    name = "Команда"
    name_plural = "Команды"
    category = "🏢 Компания"
    icon = "fa-solid fa-users"

    column_list = [Team.id, Team.name, Team.join_code]
    column_labels = {
        Team.id: "ID",
        Team.name: "Название команды",
        Team.join_code: "Код приглашения",
    }


class TaskAdmin(ModelView, model=Task):
    name = "Задача"
    name_plural = "Задачи"
    category = "📋 Рабочий процесс"
    icon = "fa-solid fa-list-check"

    column_list = [
        Task.id,
        Task.title,
        Task.status,
        Task.deadline,
        Task.team_id,
        Task.assignee_id,
    ]
    column_labels = {
        Task.id: "ID",
        Task.title: "Название",
        Task.status: "Статус",
        Task.deadline: "Дедлайн",
        Task.team_id: "Команда",
        Task.assignee_id: "Исполнитель (ID)",
    }


class MeetingAdmin(ModelView, model=Meeting):
    name = "Встреча"
    name_plural = "Встречи"
    category = "📋 Рабочий процесс"
    icon = "fa-solid fa-calendar-days"

    column_list = [
        Meeting.id,
        Meeting.title,
        Meeting.start_time,
        Meeting.end_time,
        Meeting.user_id,
    ]
    column_labels = {
        Meeting.id: "ID",
        Meeting.title: "Тема встречи",
        Meeting.start_time: "Начало",
        Meeting.end_time: "Конец",
        Meeting.user_id: "Организатор (ID)",
    }


class EvaluationAdmin(ModelView, model=Evaluation):
    name = "Оценка"
    name_plural = "Оценки"
    category = "⭐ Эффективность"
    icon = "fa-solid fa-star"

    column_list = [
        Evaluation.id,
        Evaluation.score,
        Evaluation.task_id,
        Evaluation.user_id,
    ]
    column_labels = {
        Evaluation.id: "ID",
        Evaluation.score: "Балл (1-5)",
        Evaluation.task_id: "Задача (ID)",
        Evaluation.user_id: "Сотрудник (ID)",
    }


class CommentAdmin(ModelView, model=Comment):
    name = "Комментарий"
    name_plural = "Комментарии"
    category = "📋 Рабочий процесс"
    icon = "fa-solid fa-comments"

    column_list = [
        Comment.id,
        Comment.text,
        Comment.created_at,
        Comment.task_id,
        Comment.user_id,
    ]
    column_labels = {
        Comment.id: "ID",
        Comment.text: "Текст",
        Comment.created_at: "Дата создания",
        Comment.task_id: "Задача (ID)",
        Comment.user_id: "Автор (ID)",
    }
