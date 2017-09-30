from odoo.tests.common import TransactionCase
from unittest.mock import PropertyMock, patch
from datetime import datetime


class BadTestCase(TransactionCase):
    def test_xml_data(self):
        """ Test that the data are properly loaded """
        stage_open = self.env.ref('shift_management.open')
        self.assertEqual(stage_open._name, 'shift.stage', "Wrong table")
        self.assertEqual(stage_open.name, 'Confirmed', "Wrong name")
        self.assertEqual(stage_open.code, 'open', "Wrong code")
 
class IntegrationTestCase(TransactionCase):
    def test_shift_generation(self):
        """ Check generation of shift based on a planning """
        self.env.user.tz = 'Europe/Brussels' #Make sure about the timezone of the user
        worker_1 = self.env['res.partner'].create({'name': 'worker1'})
        worker_2 = self.env['res.partner'].create({'name': 'worker2'})
        worker_3 = self.env['res.partner'].create({'name': 'worker3'})
        planning_id = self.env['shift.planning'].create({'name': 'Test Planning'})
 
        task_template_id = self.env['shift.template'].create({
            'name': 'test_task',
            'planning_id': planning_id.id,
            'day_nb_id': self.env['shift.daynumber'].create({'number': 2}).id,
            'start_time': 7.5,
            'end_time': 10.5,
            'duration': 3,
            'worker_nb': 5,
            'worker_ids': [(6, 0, [worker_1.id, worker_2.id, worker_3.id])],
        })
 
        generation_plannig_wizard_id = self.env['shift.generate_planning'].create({
            'date_start': '2017-01-01',
            'planning_id': planning_id.id,
        })
        res = generation_plannig_wizard_id.generate_task()
        #self.assertEqual(res['domain'],  [('id', 'in', [1, 2, 3, 4, 5])], 'Domain miss match')
        task_ids = res['domain'][0][2]
        self.assertEqual(len(task_ids), 5, 'Correct number of task not created')
        tasks = self.env['shift.shift'].browse(task_ids)
        #Check date and time is correct
        self.assertTrue(all([time == '2017-01-02 06:30:00' for time in tasks.mapped('start_time')]), "Bad start time")
        self.assertTrue(all([task_t == task_template_id for task_t in tasks.mapped('task_template_id')]), "Task not linked properly to his template")
        #Test worker assignation
        self.assertTrue(any([t.worker_id == worker_1 for t in tasks]), "Worker 1 Not assigned, he should be")
        self.assertTrue(any([t.worker_id == worker_2 for t in tasks]), "Worker 2 Not assigned, he should be")
        self.assertTrue(any([t.worker_id == worker_3 for t in tasks]), "Worker 3 Not assigned, he should be")
        self.assertEqual(len([t for t in tasks if not t.worker_id]), 2, "Two free slot should remain")

class UnitTestCase(TransactionCase):
    def setUp(self):
        super(UnitTestCase, self).setUp()
        self.task_template = self.env.ref('shift_management.template_demo1')
        self.draft_stage = self.env.ref('shift_management.draft')

    def test_shift_generation_return(self):
        """ Test that generate_task return the proper domain """
        with patch("odoo.addons.shift_management.models.planning.TaskTemplate._generate_task_day") as my_mock:
            type(my_mock()).ids = PropertyMock(return_value=[1,2,3,4])
            generation_plannig_wizard_id = self.env['shift.generate_planning'].new()
            res = generation_plannig_wizard_id.generate_task()
            self.assertEqual(res['domain'],  [('id', 'in', [1, 2, 3, 4])], "Domain does not match")
            my_mock.assert_called_with()
 
    def test_shift_generation_context(self):
        with patch("odoo.addons.shift_management.wizard.instanciate_planning.InstanciatePlanning.with_context") as my_mock:
            generation_plannig_wizard_id = self.env['shift.generate_planning'].new({'date_start': '2017-09-10'})
            generation_plannig_wizard_id.generate_task()
            my_mock.assert_called_with(visualize_date='2017-09-10')
 
    def test_task_generation_number(self):
        """ Test that the correct number of task is generated """
        tasks = self.task_template._generate_task_day()
        self.assertEqual(len(tasks), 5, "Number of task generated is not correct")
         
    def test_task_generation_copy(self):
        """ Check that value is correctly copy from the template """
        with patch("odoo.addons.shift_management.models.planning.TaskTemplate._get_datetime_timezone", 
                   return_value=('2017-01-01 10:00:00', '2017-01-01 13:00:00')):
              
            tasks = self.task_template ._generate_task_day()
            for t in tasks:
                self.assertEqual(t.task_template_id, self.task_template , "Task Template is wrong")
                self.assertEqual(t.start_time, self.task_template .start_date, "Start Time is wrong")
                self.assertEqual(t.end_time, self.task_template .end_date, "End Time is wrong")
                self.assertEqual(t.super_coop_id, self.task_template .super_coop_id, "Super Coop is wrong")
                self.assertEqual(t.stage_id, self.draft_stage, "Stage should be draft")
        #Change the code to make it easier to patch
        #Now we know that start time is copied properly we can check it
    
    def test_date_computation(self):
        """ Test date computation """
        self.env.user.tz = 'Europe/Brussels'
        today = datetime.strptime("2017-10-02", "%Y-%m-%d")
        start_date, end_date = self.env['shift.template']._get_datetime_timezone(today, 4, 9.0, 11.5)
        self.assertTrue(start_date, datetime(2017, 10, 5, 7))
        self.assertTrue(end_date, datetime(2017, 10, 5, 9, 30))
 
    def test_task_assignation(self):
        """ Check that regular worker are assign Properly """
        tasks = self.task_template ._generate_task_day()
        self.assertEqual(len([t for t in tasks if not t.worker_id]), 
                         self.task_template.worker_nb - len(self.task_template.worker_ids), 
                         "Wrong number of free slot")
        for worker in self.task_template.worker_ids:
            self.assertTrue(any([t.worker_id == worker for t in tasks]), 
                            "%s Not assigned, he should be" % worker.name)
 
    def test_task_template_date(self):
        """ Check that start_time is properly computed based on the context """
        self.env.user.tz = 'Europe/Brussels' #Make sure about the timezone of the user
        task_template = self.task_template .with_context(visualize_date='2016-02-28')
        #Should be the next day 29 of Feb with -1 Hour in UTC
        self.assertEqual(task_template.start_date, "2016-02-29 06:30:00", "Start date is wrong")
        self.assertEqual(task_template.end_date, "2016-02-29 09:30:00", "End date is wrong")
