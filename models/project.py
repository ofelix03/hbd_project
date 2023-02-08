# -*- coding: utf-8 -*-
from openerp import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    open_tasks_count = fields.Integer(string="Open")
    delayed_tasks_count = fields.Integer(string="Delay")
    finished_tasks_current_month_count = fields.Integer(string="Finish Month")
    finished_tasks_current_past_week_count = fields.Integer(string="Finish Week")

    def compute_tasks_stats(self):
        for project in self:
            project.tasks.compute_task_state()

            open_tasks_count = len(
                project.tasks.filtered(lambda task: task.is_open_task)
            )
            finished_tasks_current_past_week_count = len(
                project.tasks.filtered(lambda task: task.is_finished_task_past_week)
            )
            finished_tasks_current_month_count = len(
                project.tasks.filtered(lambda task: task.is_finished_task_current_month)
            )
            delayed_tasks_count = len(
                project.tasks.filtered(lambda task: task.is_delayed_task)
            )
            project.write(
                {
                    "open_tasks_count": open_tasks_count,
                    "finished_tasks_current_past_week_count": finished_tasks_current_past_week_count,
                    "finished_tasks_current_month_count": finished_tasks_current_month_count,
                    "delayed_tasks_count": delayed_tasks_count,
                }
            )

    def _cron_compute_tasks_stats(self, cr, uid, context=None):
        ids = self.pool["project.project"].search(cr, uid, [], context=context)
        projects = self.pool["project.project"].browse(cr, uid, ids)
        for project in projects:
            project.compute_tasks_stats()
