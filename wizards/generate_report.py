from openerp import api, fields, models


class GenerateReport(models.TransientModel):
    _name = "hbd.generate.report"

    def generate_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        return self.pool["report"].get_action(
            cr, uid, [], "hbd_project.report_project_task", data=None, context=context
        )
