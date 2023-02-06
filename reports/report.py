from openerp import api, models, fields


class ProjectTaskReport(models.AbstractModel):
    _name = 'report.hbd_project.report_project_task'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('hbd_project.report_project_task')

        data = self._build_report_data()

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': [data],
        }
        return report_obj.render('hbd_project.report_project_task', docargs)

    def _build_report_data(self):
        tasks = self.env['project.task'].search([])
        users = tasks.mapped(lambda task: task.user_id)
        data = []
        for user in users:
            data.append({
                'user_id': user.id,
                'user_name': user.name,
                'tasks': []
            })

        for d in data:
            user_tasks = self.env['project.task'].search([('user_id', '=',
                                                           d['user_id'])])
            d['tasks'] = user_tasks

        return data
