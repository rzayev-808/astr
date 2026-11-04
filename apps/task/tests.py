from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from pricing.models import Pricing
from space.models import Space
from squads.models import Squad
from task.models import Comment, Project, Task
from user.models import User


def client_for(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


class TaskAccessTests(TestCase):
    """Task-ı yalnız girişi olan görür/silir/yaradır: space yaradanı/üzvü, squad üzvü, task üzvü."""

    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner")
        self.member = User.objects.create(email="member@test.az", fullname="Member")
        self.task_member = User.objects.create(email="tm@test.az", fullname="TM")
        self.stranger = User.objects.create(email="x@test.az", fullname="X")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.space.members.add(self.member)
        self.squad = Squad.objects.create(name="Alpha", space=self.space)
        self.squad_member = User.objects.create(email="sq@test.az", fullname="Sq")
        self.squad.squad_members.add(self.squad_member)
        self.project = Project.objects.create(name="P")
        self.task = Task.objects.create(name="T1", squad=self.squad, deadline=timezone.now(),
                                        project=self.project, description="d", story_point="3")
        self.task.members.add(self.task_member)
        self.url = f"/task/api/{self.task.id}/"

    def test_anonymous_is_rejected(self):
        self.assertIn(APIClient().get("/task/api/").status_code, (401, 403))
        self.assertIn(APIClient().delete(self.url).status_code, (401, 403))
        self.assertTrue(Task.objects.filter(pk=self.task.id).exists())

    def test_owner_space_member_squad_member_and_task_member_can_see(self):
        for u in (self.owner, self.member, self.squad_member, self.task_member):
            self.assertEqual(client_for(u).get(self.url).status_code, 200, u.email)
            self.assertIn(self.task.id, [t["id"] for t in client_for(u).get("/task/api/").json()])

    def test_stranger_cannot_see_or_delete(self):
        # login olub, amma bu space-də deyil → başqa space-in squad task-larını görmür
        c = client_for(self.stranger)
        self.assertEqual(c.get(self.url).status_code, 404)
        self.assertEqual(c.get("/task/api/").json(), [])
        self.assertEqual(c.get(f"/task/api/?squad_id={self.squad.id}").json(), [])
        self.assertEqual(c.delete(self.url).status_code, 404)
        self.assertEqual(c.delete(f"/task/api/action/{self.task.id}").status_code, 404)
        self.assertTrue(Task.objects.filter(pk=self.task.id).exists())

    def test_create_only_in_accessible_squad(self):
        body = {"name": "New", "squad": self.squad.id, "deadline": "2030-01-01T10:00:00Z",
                "project": self.project.id, "description": "d", "story_point": "1"}
        self.assertEqual(client_for(self.stranger).post("/task/api/create/", body, format="json").status_code, 403)
        # dəvətlə gələn space üzvü squad-da task yarada bilir
        for u in (self.member, self.squad_member, self.owner):
            self.assertEqual(client_for(u).post("/task/api/create/", body, format="json").status_code, 201, u.email)

    def test_comment_only_on_accessible_task(self):
        body = {"user": self.stranger.id, "task": self.task.id, "comment": "hi"}
        self.assertEqual(client_for(self.stranger).post("/task/api/add/comment/", body, format="json").status_code, 403)
        body = {"user": self.member.id, "task": self.task.id, "comment": "hi"}
        self.assertEqual(client_for(self.member).post("/task/api/add/comment/", body, format="json").status_code, 201)
        self.assertEqual(Comment.objects.filter(task=self.task).count(), 1)
