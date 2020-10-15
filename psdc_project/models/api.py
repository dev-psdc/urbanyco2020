# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
import logging
_logger = logging.getLogger(__name__)


class ProjectsList(models.Model):
    """
    List projects public and followers allowed
    example to use:
    # List all actives projects 
    projects = env['psdc_project.projects_list'].search(['|', '&', ('privacy_visibility', '=', 'followers'), ('partner_id', '=', 6), '&', ('privacy_visibility', '=', 'employees'), ('partner_id', '=', None)])
    # Searh project by keyword
    projects = env['psdc_project.projects_list'].search(['|', '|', ('project_name', 'ilike', keyword), ('resident_name', 'ilike', keyword), ('qr_token', 'ilike', keyword)])
    """
    _name = 'psdc_project.projects_list'
    _auto = False
    _order = 'create_date desc'
    id = fields.Integer(string='ID', readonly=True)
    project_id = fields.Integer(string='Project ID', readonly=True)
    resident_id = fields.Integer(string='Resident ID', readonly=True)
    partner_id = fields.Integer(string='Partner ID', readonly=True)
    partner_name = fields.Char(string='Partner Name', readonly=True)
    project_name = fields.Char(string='Project Name', readonly=True)
    qr_token = fields.Char(string='QR Token', readonly=True)
    resident_name = fields.Char(string='Resident Name', readonly=True)
    privacy_visibility = fields.Char(string='Privacy Visibility', readonly=True)
    create_date = fields.Datetime(string='Create Date', readonly=True)
    tasks_completed_total = fields.Integer(string='Tasks Completed Total', readonly=True)
    tasks_total = fields.Integer(string='Tasks Total', readonly=True)
    qr_code = fields.Binary(string='QR Code', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'psdc_project_projects_list')
        self._cr.execute("""
            CREATE OR REPLACE VIEW psdc_project_projects_list AS
            SELECT 
                row_number() OVER (order by PP.id) AS id,
                PP.id AS project_id,
                PP.resident_id AS resident_id,
                CASE
                    WHEN PP.privacy_visibility LIKE 'employees' THEN NULL
                    WHEN PP.privacy_visibility LIKE 'followers' THEN MF.partner_id
                END AS partner_id,
                AAA.name AS project_name,
                CASE
                    WHEN PP.privacy_visibility LIKE 'employees' THEN NULL
                    WHEN PP.privacy_visibility LIKE 'followers' THEN RP2.name
                END AS partner_name,
                PP.qr_token AS qr_token,
                RP.name AS resident_name,
                PP.privacy_visibility AS privacy_visibility,
                PP.create_date AS create_date,
                (
                    SELECT
                        COUNT(PT.id)
                    FROM
                        project_task PT
                    WHERE 
                        PT.project_id = PP.id
                        AND PT.kanban_state LIKE 'done'
                ) as tasks_completed_total,
                (
                    SELECT
                        COUNT(PT.id)
                    FROM
                        project_task PT
                    WHERE 
                        PT.project_id = PP.id
                ) as tasks_total,
                PP.qr_code AS qr_code
            FROM
                project_project PP
                INNER JOIN res_partner RP ON RP.id = PP.resident_id
                INNER JOIN account_analytic_account AAA ON AAA.id = PP.analytic_account_id
                LEFT JOIN mail_followers MF ON MF.res_id = PP.id AND MF.res_model LIKE 'project.project'
                LEFT JOIN res_partner RP2 ON RP2.id = MF.partner_id
            WHERE
                PP.active IS TRUE
                AND PP.privacy_visibility IN ('followers', 'employees')""")


class TasksList(models.Model):
    """
    Active tasks list
    example to use:
    # Lists tasks by project
    tasks = env['psdc_project.tasks_list'].search_read([('project_id', '=', 3)])
    # Searh project by keyword
    projects = env['psdc_project.tasks_list'].search([('project_id', '=', 3), '|', '|', '|', ('project_name', 'ilike', keyword), ('task_name', 'ilike', keyword), ('resident_name', 'ilike', keyword), ('qr_token', 'ilike', keyword)])
    """
    _name = 'psdc_project.tasks_list'
    _auto = False
    _order = 'create_date desc'
    id = fields.Integer(string='ID', readonly=True)
    project_id = fields.Integer(string='Project ID', readonly=True)
    subproject_id = fields.Integer(string='Sub Project ID', readonly=True)
    user_id = fields.Integer(string='User ID', readonly=True)
    resident_id = fields.Integer(string='Resident ID', readonly=True)
    task_name = fields.Char(string='Task Name', readonly=True)
    project_name = fields.Char(string='Project Name', readonly=True)
    subproject_name = fields.Char(string='Sub Project Name', readonly=True)
    resident_name = fields.Char(string='Resident Name', readonly=True)
    username = fields.Char(string='Username', readonly=True)
    description = fields.Text(string='Description', readonly=True)
    kanban_state = fields.Char(string='Kanban State', readonly=True)
    kanban_state_formatted = fields.Char(string='Kanban State Formatted', readonly=True)
    create_date = fields.Datetime(string='Create Date', readonly=True)
    progress = fields.Float(string='Progress', readonly=True)
    qr_token = fields.Char(string='QR Token', readonly=True)
    qr_code = fields.Binary(string='QR Code', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'psdc_project_tasks_list')
        self._cr.execute("""
            CREATE OR REPLACE VIEW psdc_project_tasks_list AS
            SELECT
                PT.id AS id,
                PT.project_id AS project_id,
                PT.subproject_id AS subproject_id,
                PT.user_id AS user_id,
                PP.resident_id AS resident_id,
                PT.name AS task_name,
                AAA.name AS project_name,
                PPS.name AS subproject_name,
                RP1.name AS resident_name,
                RP2.name AS username,
                PT.description  AS description,
                PT.kanban_state AS kanban_state,
                CASE 
                    WHEN PT.kanban_state LIKE 'done' THEN 'Listo'
                    WHEN PT.kanban_state LIKE 'normal' THEN 'En proceso'
                    WHEN PT.kanban_state LIKE 'blocked' THEN 'Bloqueado'
                END AS kanban_state_formatted,
                PT.create_date AS create_date,
                PT.progress AS progress,
                PT.qr_token AS qr_token,
                pt.qr_code AS qr_code
            FROM
                project_task PT
                INNER JOIN project_project PP ON PP.id = PT.project_id
                INNER JOIN account_analytic_account AAA ON AAA.id = PP.analytic_account_id
                INNER JOIN res_partner RP1 ON RP1.id = PP.resident_id
                INNER JOIN res_users RS ON RS.id = PT.user_id
                INNER JOIN res_partner RP2 ON RP2.id = RS.partner_id
                LEFT JOIN psdc_project_subproject PPS ON PPS.id = PT.subproject_id
            WHERE
                PT.active iS TRUE""")


class PlanningsList(models.Model):
    """
    Plannings lists
    example to use:
    # Lists plannings by user_id
    plannings = env['psdc_project.plannings_list'].search_read([('user_id', '=', 6)])
    """
    _name = 'psdc_project.plannings_list'
    _auto = False
    _order = 'planning_create_date desc'
    id = fields.Integer(string='ID', readonly=True)
    project_id = fields.Integer(string='Project ID', readonly=True)
    user_id = fields.Integer(string='User ID', readonly=True)
    owner_id = fields.Integer(string='Owner ID', readonly=True)
    responsible_id = fields.Integer(string='Responsible ID', readonly=True)
    resident_id = fields.Integer(string='Resident ID', readonly=True)
    project_name = fields.Char(string='Project Name', readonly=True)
    responsible_name = fields.Char(string='Responsible Name', readonly=True)
    owner_name = fields.Char(string='Owner Name', readonly=True)
    responsible_login = fields.Char(string='Responsible Login', readonly=True)
    resident_name = fields.Char(string='Resident Name', readonly=True)
    planning_state = fields.Char(string='Planning State', readonly=True)
    planning_state_formatted = fields.Char(string='Planning State', readonly=True)
    planning_create_date = fields.Datetime(string='Planning Create Date', readonly=True)
    planning_start_on = fields.Date(string='Start on', readonly=True)
    planning_end_on = fields.Date(string='End on', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'psdc_project_plannings_list')
        self._cr.execute("""
            CREATE OR REPLACE VIEW psdc_project_plannings_list AS
            SELECT
                PPP.id AS id,
                PP.id AS project_id,
                RU.id AS user_id,
                PP.user_id AS owner_id,
                RP.id AS responsible_id,
                RP3.id AS resident_id,
                AAA.name AS project_name,
                RP.name AS responsible_name,
                RP2.name AS owner_name,
                RU.login AS responsible_login,
                RP3.name AS resident_name,
                PPP.state AS planning_state,
                CASE 
                    WHEN PPP.state LIKE 'pending' THEN 'Pendiente'
                    WHEN PPP.state LIKE 'active' THEN 'Activo'
                    WHEN PPP.state LIKE 'finished' THEN 'Terminado'
                END AS planning_state_formatted,
                PPP.create_date AS planning_create_date,
                PPP.start_on AS planning_start_on,
                PPP.end_on AS planning_end_on
            FROM
                psdc_project_planning PPP
                INNER JOIN project_project PP ON PP.id = PPP.project_id
                INNER JOIN account_analytic_account AAA ON AAA.id = PP.analytic_account_id
                INNER JOIN res_partner RP ON RP.id = PPP.responsible_id
                INNER JOIN res_users RU ON RU.partner_id = RP.id
                INNER JOIN res_users RU2 ON RU2.id = PP.user_id
                INNER JOIN res_partner RP2 ON RP2.id = RU2.partner_id
                INNER JOIN res_partner RP3 ON RP3.id = PP.resident_id""")


class PlanningTasksList(models.Model):
    """
    Tasks list by planning
    example to use:
    # Lists tasks by project
    tasks = env['psdc_project.planning_tasks_list'].search_read([('planning_id', '=', 1)])
    """
    _name = 'psdc_project.planning_tasks_list'
    _auto = False
    _order = 'task_create_date desc'
    id = fields.Integer(string='ID', readonly=True)
    planning_id = fields.Integer(string='Planning ID', readonly=True)
    project_id = fields.Integer(string='Project ID', readonly=True)
    task_id = fields.Integer(string='Task ID', readonly=True)
    task_name = fields.Char(string='Task Name', readonly=True)
    task_kanban_state = fields.Char(string='Task Kanban State', readonly=True)
    task_kanban_state_formatted = fields.Char(string='Task Kanban State Formatted', readonly=True)
    project_name = fields.Char(string='Project Name', readonly=True)
    username = fields.Char(string='Username', readonly=True)
    task_progress = fields.Float(string='Task Progress', readonly=True)
    task_create_date = fields.Datetime(string='Task Create Date', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'psdc_project_planning_tasks_list')
        self._cr.execute("""
            CREATE OR REPLACE VIEW psdc_project_planning_tasks_list AS
            SELECT 
                row_number() OVER (order by PTPPPR.project_task_id) AS id,
                PTPPPR.psdc_project_planning_id AS planning_id,
                PT.project_id AS project_id,
                PT.id AS task_id,
                PT.name AS task_name,
                PT.kanban_state AS task_kanban_state,
                CASE 
                    WHEN PT.kanban_state LIKE 'done' THEN 'Listo'
                    WHEN PT.kanban_state LIKE 'normal' THEN 'En proceso'
                    WHEN PT.kanban_state LIKE 'blocked' THEN 'Bloqueado'
                END AS task_kanban_state_formatted,
                AAA.name AS project_name,
                RP2.name AS username,
                PT.progress AS task_progress,
                PT.create_date AS task_create_date
            FROM
                project_task_psdc_project_planning_rel PTPPPR
                INNER JOIN project_task PT ON PT.id = PTPPPR.project_task_id
                INNER JOIN project_project PP ON PP.id = PT.project_id
                INNER JOIN account_analytic_account AAA ON AAA.id = PP.analytic_account_id
                INNER JOIN res_users RS ON RS.id = PT.user_id
                INNER JOIN res_partner RP2 ON RP2.id = RS.partner_id""")


class TaskHistoriesList(models.Model):
    """
    Tasks histories list
    example to use:
    # Lists histories by task
    histories = env['psdc_project.task_histories_list'].search_read([('task_id', '=', 3)])
    """
    _name = 'psdc_project.task_histories_list'
    _auto = False
    _order = 'history_create_date desc'
    id = fields.Integer(string='ID', readonly=True)
    task_id = fields.Integer(string='Task ID', readonly=True)
    project_id = fields.Integer(string='Project ID', readonly=True)
    history_state = fields.Char(string='History State', readonly=True)
    history_state_formatted = fields.Char(string='History State Formatted', readonly=True)
    history_comments = fields.Text(string='History Comments', readonly=True)
    history_time = fields.Char(string='History Time', readonly=True)
    history_date = fields.Date(string='History Date', readonly=True)
    history_create_date = fields.Datetime(string='History Create Date', readonly=True)
    latitude = fields.Float(string='History latitude', readonly=True)
    longitude = fields.Float(string='History latitude', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'psdc_project_task_histories_list')
        self._cr.execute("""
            CREATE OR REPLACE VIEW psdc_project_task_histories_list AS
            SELECT 
                PPTH.id AS id,
                PPTH.task_id AS task_id,
                PT.project_id AS project_id,
                PPTH.state AS history_state,
                CASE 
                    WHEN PPTH.state LIKE 'done' THEN 'Listo'
                    WHEN PPTH.state LIKE 'normal' THEN 'En proceso'
                    WHEN PPTH.state LIKE 'blocked' THEN 'Bloqueado'
                END AS history_state_formatted,
                PPTH.comments AS history_comments,
                PPTH.time AS history_time,
                PPTH.date AS history_date,
                PPTH.create_date AS history_create_date,
                PPTH.latitude AS latitude,
                PPTH.longitude AS longitude
            FROM 
                psdc_project_task_history PPTH
                INNER JOIN project_task PT ON PT.id = PPTH.task_id""")


class TaskHistoryImagesList(models.Model):
    """
    Tasks history images list by task history image
    example to use:
    # Lists histories by task
    histories = env['psdc_project.task_history_images_list'].search_read([('task_history_id', '=', 4)])
    """
    _name = 'psdc_project.task_history_images_list'
    _auto = False
    _order = 'create_date desc'
    id = fields.Integer(string='ID', readonly=True)
    task_history_id = fields.Integer(string='Task History ID', readonly=True)
    create_date = fields.Datetime(string='Create Date', readonly=True)
    image = fields.Binary(string='Image', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'psdc_project_task_history_images_list')
        self._cr.execute("""
            CREATE OR REPLACE VIEW psdc_project_task_history_images_list AS
            SELECT 
                PPTHI.id as id,
                PPTHI.task_history_id AS task_history_id,
                PPTHI.create_date AS create_date,
                PPTHI.image AS image
            FROM 
                psdc_project_task_history_image PPTHI""")


class UserAPIDetail(models.Model):
    """
    User API detail
    example to use:
    # get User API detail
    user = env['psdc_project.user_api_detail'].search_read([('id', '=', 6)])
    """
    _name = 'psdc_project.user_api_detail'
    _auto = False
    _order = 'id asc'
    id = fields.Integer(string='ID', readonly=True)
    partner_id = fields.Integer(string='Partner ID', readonly=True)
    active = fields.Boolean(string='Is Active', readonly=True)
    login = fields.Char(string='User Login', readonly=True)
    name = fields.Char(string='Username', readonly=True)
    display_name = fields.Char(string='Display Name', readonly=True)
    email = fields.Char(string='Email', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'psdc_project_user_api_detail')
        self._cr.execute("""
            CREATE OR REPLACE VIEW psdc_project_user_api_detail AS
            SELECT
                RU.id AS id,
                RP.id AS partner_id,
                RU.active AS active,
                RU.login AS login,
                RP.name AS name,
                RP.display_name AS display_name,
                RP.email AS email
            FROM
                res_users RU
                INNER JOIN res_partner RP ON RP.id = RU.partner_id""")
