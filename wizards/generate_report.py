from openerp import api, fields, models


class GenerateReport(models.TransientModel):
    _name = 'hbd.generate.report'

    def generate_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        # datas = {'ids': context.get('active_ids', [])}
        # res = self.read(cr, uid, ids, ['date_start', 'date_end', 'user_ids'], context=context)
        # res = res and res[0] or {}
        # datas['form'] = res
        # if res.get('id',False):
        #     datas['ids']=[res['id']]
        # user_tasks = self.pool('project.task').search([])
        # users = user_tasks.mapped(lambda task: task.user_id)
        # dd = []
        # for user in users:
        #     dd.append({
        #         'user_id': user.id,
        #         'user_name': user.name,
        #         'tasks': []
        #     })
        #
        return self.pool['report'].get_action(cr, uid, [],
                                              'hbd_project.report_project_task',
                                              data=None, context=context)