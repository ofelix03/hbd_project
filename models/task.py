from datetime import date, timedelta

from openerp import api, fields, models


class Task(models.Model):
    _inherit = "project.task"

    is_open_task = fields.Boolean(default=False)
    is_delayed_task = fields.Boolean(default=False)
    is_finished_task_current_month = fields.Boolean(default=False)
    is_finished_task_past_week = fields.Boolean(default=False)

    open_tasks_count = fields.Integer(
        related="project_id.open_tasks_count",
        store=True,
        string="Open",
    )
    delayed_tasks_count = fields.Integer(
        related="project_id.delayed_tasks_count", store=True, string="Delay"
    )
    finished_tasks_current_month_count = fields.Integer(
        related="project_id.finished_tasks_current_month_count",
        store=True,
        string="Finish Month",
    )
    finished_tasks_current_past_week_count = fields.Integer(
        related="project_id.finished_tasks_current_past_week_count",
        store=True,
        string="Finish Week",
    )
    test = fields.Boolean(compute="_compute_test")

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        result = super(Task, self).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
        for line in result:
            if line.get("__domain") and "user_id" in line:
                user_tasks = self.search([("user_id", "=", line["user_id"][0])])

                open_tasks_count = len(
                    user_tasks.filtered(lambda task: task.is_open_task)
                )
                delayed_tasks_count = len(
                    user_tasks.filtered(lambda task: task.is_delayed_task)
                )
                finished_tasks_current_month_count = len(
                    user_tasks.filtered(
                        lambda task: task.is_finished_task_current_month
                    )
                )
                finished_tasks_current_past_week_count = len(
                    user_tasks.filtered(lambda task: task.is_finished_task_past_week)
                )

                line["open_tasks_count"] = open_tasks_count
                line["delayed_tasks_count"] = delayed_tasks_count
                line[
                    "finished_tasks_current_month_count"
                ] = finished_tasks_current_month_count
                line[
                    "finished_tasks_current_past_week_count"
                ] = finished_tasks_current_past_week_count

        return result

    def compute_task_state(self):
        for task in self:
            today = date.today()
            last_work_entry = task.work_ids.search(
                [("task_id", "=", task.id)], order="date desc", limit=1
            )
            last_work_entry_date = None
            finished_this_month = False
            finished_last_week = False
            if last_work_entry:
                last_work_entry_date = fields.Date.from_string(last_work_entry.date)
                finished_this_month = (
                    last_work_entry_date.month == today.month
                    and last_work_entry_date.year == today.year
                )
                last_2_weeks = today - timedelta(days=14)
                last_week = today - timedelta(days=7)
                finished_last_week = (
                    last_work_entry_date >= last_week
                    and last_work_entry_date < last_week
                )

            is_open_task = False
            is_delayed_task = False
            is_finished_task_current_month = False
            is_finished_task_current_month = False

            if task.effective_hours < task.planned_hours:
                task.write({"is_open_task": True})
            else:
                task.write({"is_open_task": False})

            if task.effective_hours > task.planned_hours:
                task.write({"is_delayed_task": True})
            else:
                task.write({"is_delayed_task": False})

            if task.effective_hours >= task.planned_hours and finished_this_month:
                task.write({"is_finished_task_current_month": True})
            else:
                task.write({"is_finished_task_current_month": False})

            if task.effective_hours >= task.planned_hours and finished_last_week:
                task.write({"is_finished_task_past_week": True})
            else:
                task.write({"is_finished_task_past_week": False})

    @api.depends("test", "stage_id", "work_ids")
    def _compute_test(self):
        # I anticipate a linear time complexity with the approach I have taken here to
        # determine the state of the various tasks of each project.
        # An optimized solution will be to employ a cron that runs every minute, checks
        # and update the count of each tasks state
        # A third option will be to use a menu action to refresh the state of every
        # project/task after they have ben selected
        for task in self:
            task.project_id.compute_tasks_stats()
